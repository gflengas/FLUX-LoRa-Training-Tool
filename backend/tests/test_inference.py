import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import httpx
from app import app
import src.services.comfy_integration as comfy
import src.api.routes as routes


class InferenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.output = Path(self.temp.name)
        for module in (comfy, routes):
            override = patch.object(module, "INFERENCE_OUTPUT", self.output)
            override.start()
            self.addCleanup(override.stop)
        self.client = app.test_client()
        self.body = {"modelId": "sd_xl_base_1.0.safetensors", "prompt": "A dog jumping over a red F1 car", "seed": 0}

    def test_invalid_settings_do_not_reach_engine(self):
        with patch.object(comfy, "call_comfy") as engine:
            for changes in ({"width": 513}, {"images": 5}, {"prompt": " "}, {"seed": -1}):
                result = self.client.post("/api/inference", json={**self.body, **changes})
                self.assertEqual(result.status_code, 400)
            self.assertEqual(self.client.post("/api/inference", data="not json").status_code, 400)
            engine.assert_not_called()

    def test_stopped_engine_returns_actionable_error(self):
        with patch.object(comfy, "call_comfy", side_effect=httpx.ConnectError("offline")):
            response = self.client.get("/api/models")
            self.assertEqual(response.status_code, 503)
            self.assertIn("Start", response.json["message"])

    def test_submission_preserves_seed_zero_and_rejects_unknown_model(self):
        job_id = str(uuid4())
        with patch.object(comfy, "get_models", return_value={"models": [{"id": "sd_xl_base_1.0.safetensors"}]}):
            with patch.object(comfy, "call_comfy", return_value={"prompt_id": job_id}) as engine:
                response = self.client.post("/api/inference", json={**self.body, "images": 2})
                self.assertEqual(response.status_code, 202)
                graph = engine.call_args.kwargs["json"]["prompt"]
                self.assertEqual(graph["10"]["inputs"]["seed"], 0)
                self.assertEqual(graph["13"]["inputs"]["seed"], 1)
                self.assertEqual(self.client.post("/api/inference", json={**self.body, "modelId": "bad"}).status_code, 400)
                self.assertEqual(self.client.post("/api/inference", json={**self.body, "loraId": "unsupported"}).status_code, 400)
                self.assertEqual(engine.call_count, 1)

    def test_completed_image_survives_engine_shutdown(self):
        job_id = str(uuid4())
        (self.output / f"{job_id}.json").write_text(json.dumps({
            "seed": 123, "settings": {"width": 1024, "height": 768, "images": 1}
        }))
        history = {job_id: {"status": {"completed": True, "status_str": "success"},
                           "outputs": {"12": {"images": [{"filename": "test.png", "subfolder": ""}]}}}}
        image = httpx.Response(200, content=b"png-image", request=httpx.Request("GET", "http://localhost/view"))
        with patch.object(comfy, "call_comfy", return_value=history), patch.object(comfy.httpx, "get", return_value=image):
            response = self.client.get(f"/api/inference/{job_id}")
            self.assertEqual(response.json["status"], "completed")
            url = response.json["images"][0]["url"]
        with patch.object(comfy, "call_comfy", side_effect=AssertionError("Engine should not be needed")):
            self.assertEqual(self.client.get(f"/api/inference/{job_id}").json["status"], "completed")
            with self.client.get(url) as image_response:
                self.assertEqual(image_response.data, b"png-image")
        self.assertEqual(self.client.get(f"/api/inference/images/{job_id}.json").status_code, 404)
        self.assertEqual(self.client.get(f"/api/inference/{uuid4()}").status_code, 404)


if __name__ == "__main__":
    unittest.main()
