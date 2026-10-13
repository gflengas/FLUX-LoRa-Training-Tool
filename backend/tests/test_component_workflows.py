import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.api.schemas import InferenceRequest
from src.services import comfy_integration as comfy
from src.services.comfy_workflows import MODEL_PROFILES


class ComponentWorkflowTests(unittest.TestCase):
    def settings(self, model_id, **changes):
        return InferenceRequest(modelId=model_id, prompt="A portrait", **{
            **MODEL_PROFILES[model_id]["defaults"], **changes})

    def test_profiles_require_all_complete_engine_visible_components(self):
        profile = MODEL_PROFILES["z-image-turbo"]
        with tempfile.TemporaryDirectory() as temp, patch.object(comfy, "MODELS_DIR", Path(temp)):
            available = {category: [profile[category]] for category in ("diffusion_models", "text_encoders", "vae")}
            header = json.dumps({"weight": {"shape": [1], "dtype": "F16", "data_offsets": [0, 2]}}).encode()
            paths = []
            for category, names in available.items():
                path = Path(temp) / category / names[0]
                path.parent.mkdir()
                path.write_bytes(struct.pack("<Q", len(header)) + header + b"\0\0")
                paths.append(path)
            def engine(method, path):
                return available.get(path.split("/")[-1], [])
            with patch.object(comfy, "call_comfy", side_effect=engine):
                self.assertEqual([m["id"] for m in comfy.get_models()["models"]], ["z-image-turbo"])
                available["vae"] = []
                self.assertEqual(comfy.get_models()["models"], [])
                available["vae"] = [profile["vae"]]
                paths[-1].write_bytes(struct.pack("<Q", len(header)) + header)
                self.assertEqual(comfy.get_models()["models"], [])

    def test_each_workflow_links_resolve_and_outputs_match_polling_contract(self):
        for model_id in MODEL_PROFILES:
            graph = comfy.create_workflow(self.settings(model_id, images=4), 4294967295)
            for node in graph.values():
                for value in node["inputs"].values():
                    if isinstance(value, list):
                        self.assertIn(value[0], graph)
            self.assertEqual([graph[str(12 + i * 3)]["class_type"] for i in range(4)], ["SaveImage"] * 4)
            if model_id == "z-image-turbo":
                self.assertEqual(graph["13"]["inputs"]["seed"], 0)
            else:
                self.assertEqual(graph["41"]["inputs"]["noise_seed"], 0)
            latent = graph["4"]["class_type"]
            expected = {"z-image-turbo": "EmptySD3LatentImage", "flux-2-klein-base-4b": "EmptyFlux2LatentImage",
                        "qwen-image-2.1-turbo": "EmptyLatentImage"}[model_id]
            self.assertEqual(latent, expected)

    def test_qwen_turbo_uses_official_eight_step_schedule(self):
        graph = comfy.create_workflow(self.settings("qwen-image-2.1-turbo"), 42)
        sigmas = [float(s) for s in graph["9"]["inputs"]["sigmas"].split(",")]
        self.assertEqual(len(sigmas), 9)
        self.assertEqual(sigmas[0], 1)
        self.assertEqual(sigmas[-1], 0)
        self.assertTrue(all(a > b for a, b in zip(sigmas, sigmas[1:])))
        self.assertEqual(graph["30"]["inputs"]["negative"], ["2", 1])
        for changes in ({"steps": 30}, {"guidance": 7}, {"negativePrompt": "blur"}):
            with self.assertRaises(ValueError):
                comfy.create_workflow(self.settings("qwen-image-2.1-turbo", **changes), 42)


if __name__ == "__main__":
    unittest.main()
