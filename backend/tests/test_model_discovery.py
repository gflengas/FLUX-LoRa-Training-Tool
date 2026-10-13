import json
import math
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.services import comfy_integration as comfy


class ModelDiscoveryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.checkpoints = self.root / "checkpoints"
        self.checkpoints.mkdir()
        override = patch.object(comfy, "MODELS_DIR", self.root)
        override.start()
        self.addCleanup(override.stop)
        self.shapes = {
            "model.diffusion_model.input_blocks.0.0.weight": [320, 4, 3, 3],
            "model.diffusion_model.input_blocks.4.1.transformer_blocks.0.attn2.to_k.weight": [640, 2048],
            "conditioner.embedders.0.transformer.text_model.embeddings.token_embedding.weight": [49408, 768],
            "conditioner.embedders.1.model.token_embedding.weight": [49408, 1280],
            "first_stage_model.decoder.conv_out.weight": [3, 128, 3, 3],
        }

    def checkpoint(self, name, shapes=None):
        # Sparse fixtures represent signatures, without allocating real model weights.
        header, offset = {}, 0
        for key, shape in (self.shapes if shapes is None else shapes).items():
            end = offset + math.prod(shape) * 2
            header[key] = {"shape": shape, "dtype": "F16", "data_offsets": [offset, end]}
            offset = end
        encoded = json.dumps(header).encode()
        path = self.checkpoints / name
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as file:
            file.write(struct.pack("<Q", len(encoded)))
            file.write(encoded)
            file.truncate(8 + len(encoded) + offset)
        return path

    def discover(self, names):
        with patch.object(comfy, "call_comfy", side_effect=lambda method, path: names if path == "/models/checkpoints" else []):
            return comfy.get_models()

    def test_detects_multiple_models_with_arbitrary_names_and_subfolders(self):
        self.checkpoint("portrait_v2.safetensors")
        self.checkpoint("custom/another-name.safetensors")
        self.checkpoint("not-in-engine.safetensors")
        catalog = self.discover(["portrait_v2.safetensors", "custom/another-name.safetensors"])
        self.assertEqual([item["id"] for item in catalog["models"]],
                         ["custom/another-name.safetensors", "portrait_v2.safetensors"])
        self.assertTrue(catalog["inferenceAvailable"])
        self.assertEqual(catalog["models"][1]["name"], "portrait v2")

    def test_wrong_architecture_missing_components_and_inpainting_are_excluded(self):
        self.checkpoint("named_sdxl_but_not_sdxl.safetensors", {"flux.weight": [4, 4]})
        incomplete = dict(self.shapes)
        del incomplete["first_stage_model.decoder.conv_out.weight"]
        self.checkpoint("missing-vae.safetensors", incomplete)
        inpainting = dict(self.shapes)
        inpainting["model.diffusion_model.input_blocks.0.0.weight"] = [320, 9, 3, 3]
        self.checkpoint("inpainting.safetensors", inpainting)
        names = [path.name for path in self.checkpoints.iterdir()]
        self.assertEqual(self.discover(names)["models"], [])

    def test_partial_corrupt_and_outside_files_do_not_break_discovery(self):
        partial = self.checkpoint("partial.safetensors")
        with partial.open("r+b") as file:
            file.truncate(partial.stat().st_size - 1)
        (self.checkpoints / "broken.safetensors").write_bytes(b"broken")
        self.checkpoint("../outside.safetensors")
        self.checkpoint("valid.safetensors")
        names = ["partial.safetensors", "broken.safetensors", "../outside.safetensors", "valid.safetensors"]
        self.assertEqual([item["id"] for item in self.discover(names)["models"]], ["valid.safetensors"])

    def test_changes_and_removals_are_detected_without_restarting(self):
        name = "new-model.safetensors"
        self.assertFalse(self.discover([name])["inferenceAvailable"])
        path = self.checkpoint(name)
        self.assertTrue(self.discover([name])["inferenceAvailable"])
        self.checkpoint(name, {"other.weight": [2, 2]})
        self.assertFalse(self.discover([name])["inferenceAvailable"])
        self.checkpoint(name)
        self.assertTrue(self.discover([name])["inferenceAvailable"])
        path.unlink()
        self.assertFalse(self.discover([name])["inferenceAvailable"])


if __name__ == "__main__":
    unittest.main()
