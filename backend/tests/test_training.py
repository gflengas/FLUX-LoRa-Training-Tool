import json
from pathlib import Path
from subprocess import CompletedProcess
import tempfile
import unittest
from unittest.mock import patch
from uuid import uuid4

from PIL import Image
from app import app
import src.api.routes as routes
import src.services.ai_toolkit_integration as training


def result(stdout="", code=0, stderr=""):
    return CompletedProcess([], code, stdout, stderr)


class TrainingTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for module in (training, routes):
            for name, relative in (("MODELS_DIR", "models"),
                                   ("TRAINING_DIR", "jobs"), ("TRAINING_OUTPUT", "output")):
                if hasattr(module, name):
                    override = patch.object(module, name, self.root / relative)
                    override.start()
                    self.addCleanup(override.stop)
        self.dataset = self.root / "dataset"
        self.dataset.mkdir()
        self.client = app.test_client()
        self.body = {"engine": "local", "modelInfo": {"name": "person_xyz", "type": "human"},
                     "datasetPath": str(self.dataset)}

    def prepare_images(self):
        Image.new("RGB", (512, 512), "red").save(self.dataset / "photo.png")
        (self.dataset / "photo.txt").write_text("person_xyz wearing a red shirt")

    def start(self):
        self.prepare_images()
        with patch.object(training, "call_docker", return_value=result()) as docker:
            response = self.client.post("/api/training/start", json=self.body)
        self.assertEqual(response.status_code, 202, response.json)
        return response.json, docker

    def test_folder_browser_returns_directories_and_validates_paths(self):
        (self.dataset / "portraits").mkdir()
        (self.dataset / ".hidden").mkdir()
        (self.dataset / "photo.txt").write_text("caption")
        (self.dataset / "linked").symlink_to(self.root, target_is_directory=True)
        with patch.object(training, "call_docker") as docker:
            response = self.client.get("/api/training/folders", query_string={"path": str(self.dataset)})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json["path"], str(self.dataset))
            self.assertEqual(response.json["parent"], str(self.root))
            self.assertEqual(response.json["folders"], [{"name": "portraits", "path": str(self.dataset / "portraits")}])
            for path, expected in (("relative", 400), (str(self.dataset / "missing"), 404),
                                   (str(self.dataset / "photo.txt"), 400), ("/bad\0path", 400)):
                response = self.client.get("/api/training/folders", query_string={"path": path})
                self.assertEqual(response.status_code, expected)
            docker.assert_not_called()

    def test_local_validation_never_calls_cloud_or_docker(self):
        with patch.object(training, "call_docker") as docker, patch.object(routes, "train_LoRa_with_api") as cloud:
            for changes in ({"settings": {"steps": -1}}, {"settings": {"resolution": "513"}},
                            {"settings": {"learningRate": float("nan")}},
                            {"settings": {"autoCaptioning": True}},
                            {"modelInfo": {"name": "../../escape"}}, {"modelId": "qwen"}, {"engine": "unknown"}):
                response = self.client.post("/api/training/start", json={**self.body, **changes})
                self.assertEqual(response.status_code, 400, response.json)
            docker.assert_not_called()
            cloud.assert_not_called()

    def test_dataset_rejects_missing_captions_symlinks_and_nonlocal_paths(self):
        self.prepare_images()
        (self.dataset / "photo.txt").unlink()
        with patch.object(training, "call_docker", return_value=result()) as docker:
            response = self.client.post("/api/training/start", json=self.body)
            self.assertEqual(response.status_code, 400, response.json)
            self.assertFalse(any(call.args[0] == "create" for call in docker.call_args_list))
        outside = self.root / "caption.txt"
        outside.write_text("caption")
        (self.dataset / "photo.txt").symlink_to(outside)
        with patch.object(training, "call_docker", return_value=result()):
            response = self.client.post("/api/training/start", json=self.body)
            self.assertEqual(response.status_code, 400)
            for path in ("relative/dataset", "/", str(self.root / "missing")):
                response = self.client.post("/api/training/start", json={**self.body, "datasetPath": path})
                self.assertEqual(response.status_code, 400)

    def test_submission_maps_settings_and_preserves_captions(self):
        job, docker = self.start()
        folder = training.TRAINING_DIR / job["trainingId"]
        self.assertEqual((folder / "dataset/image_0000.txt").read_text(), "person_xyz wearing a red shirt")
        config = json.loads((folder / "config.json").read_text())["config"]["process"][0]
        self.assertEqual(config["train"]["lr"], 1e-4)
        self.assertEqual(config["network"]["linear"], 16)
        self.assertEqual(config["datasets"][0]["resolution"], [512])
        self.assertEqual(config["model"]["arch"], "zimage")
        self.assertIn("_bf16", config["model"]["name_or_path"])
        self.assertIn("_v2.safetensors", config["model"]["assistant_lora_path"])
        self.assertEqual(config["sample"]["guidance_scale"], 1)
        create = next(call.args for call in docker.call_args_list if call.args[0] == "create")
        self.assertIn("SEED=42", create)
        self.assertNotIn("--rm", create)

    def test_unavailable_and_busy_engines(self):
        with patch.object(training, "call_docker", return_value=result(code=1)):
            self.assertEqual(self.client.post("/api/training/start", json=self.body).status_code, 503)
        with patch.object(training, "call_docker", side_effect=[result(), result(code=1)]):
            response = self.client.post("/api/training/start", json=self.body)
            self.assertEqual(response.status_code, 503)
            self.assertIn("build trainer", response.json["message"])
        for calls in ([result(), result(), result("active")],
                      [result(), result(), result(), result("comfy")]):
            with patch.object(training, "call_docker", side_effect=calls):
                self.assertEqual(self.client.post("/api/training/start", json=self.body).status_code, 409)

    def test_exit_zero_without_artifact_is_failed(self):
        job, _ = self.start()
        state = {"Running": False, "Status": "exited", "ExitCode": 0}
        with patch.object(training, "call_docker", side_effect=[result(json.dumps(state)), result("finished")]):
            response = self.client.get(job["trainingUrl"])
        self.assertEqual(response.json["status"], "failed")
        self.assertEqual(response.json["logs"], "finished")

    def test_completion_survives_docker_shutdown_and_returns_local_path(self):
        job, _ = self.start()
        output = training.TRAINING_OUTPUT / job["trainingId"] / job["name"] / f"{job['name']}.safetensors"
        output.parent.mkdir(parents=True)
        output.write_bytes(b"fake adapter for transport test")
        state = {"Running": False, "Status": "exited", "ExitCode": 0}
        with patch.object(training, "call_docker", side_effect=[result(json.dumps(state)), result("trained")]):
            response = self.client.get(job["trainingUrl"])
        self.assertEqual(response.json["status"], "completed")
        with patch.object(training, "call_docker", side_effect=AssertionError("Docker must not be needed")):
            self.assertEqual(self.client.get(job["trainingUrl"]).json["status"], "completed")
            self.assertEqual(Path(response.json["loraPath"]).read_bytes(), output.read_bytes())
            self.assertNotIn("modelUrl", response.json)

    def test_cancellation_and_missing_job(self):
        job, _ = self.start()
        with patch.object(training, "call_docker", return_value=result()) as docker:
            response = self.client.post(job["trainingUrl"] + "/cancel")
            self.assertEqual(response.json["status"], "cancelled")
            docker.assert_called_once_with("stop", "--time", "15", f"lora-training-{job['trainingId']}", timeout=25)
        with patch.object(training, "call_docker", side_effect=AssertionError("Already cancelled")):
            self.assertEqual(self.client.get(job["trainingUrl"]).json["status"], "cancelled")
        self.assertEqual(self.client.get(f"/api/training/{uuid4()}").status_code, 404)

    def test_docker_disconnect_does_not_mark_job_failed(self):
        job, _ = self.start()
        with patch.object(training, "call_docker", return_value=result(code=1)):
            self.assertEqual(self.client.get(job["trainingUrl"]).status_code, 503)
        self.assertEqual(training.read_job(job["trainingId"])["status"], "running")

    def test_launch_failure_retains_identity_for_recovery(self):
        self.prepare_images()
        with patch.object(training, "call_docker", side_effect=[
            result(), result(), result(), result(), result(), result(code=1, stderr="GPU runtime error"),
        ]):
            response = self.client.post("/api/training/start", json=self.body)
        self.assertEqual(response.status_code, 503)
        self.assertIn("/api/training/", response.json["message"])
        stored = list(training.TRAINING_DIR.glob("*/job.json"))
        self.assertEqual(len(stored), 1)
        self.assertEqual(json.loads(stored[0].read_text())["status"], "failed")

    def test_nonzero_exit_never_publishes_checkpoint(self):
        job, _ = self.start()
        output = training.TRAINING_OUTPUT / job["trainingId"] / job["name"] / f"{job['name']}.safetensors"
        output.parent.mkdir(parents=True)
        output.write_bytes(b"checkpoint before failure")
        state = {"Running": False, "Status": "exited", "ExitCode": 137, "OOMKilled": True}
        with patch.object(training, "call_docker", side_effect=[result(json.dumps(state)), result("out of memory")]):
            response = self.client.get(job["trainingUrl"])
        self.assertEqual(response.json["status"], "failed")
        self.assertNotIn("modelUrl", response.json)


if __name__ == "__main__":
    unittest.main()
