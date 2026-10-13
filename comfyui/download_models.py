"""Download the three supported component packages into the repository's models folder."""
import hashlib
import json
import subprocess
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = Path(__file__).with_name("models.json")


def download_model(item):
    path = ROOT / item["destination"]
    path.parent.mkdir(parents=True, exist_ok=True)
    partial = path.with_suffix(".safetensors.part")
    if path.exists():
        partial = path
    else:
        print(f"Downloading {path.name}", flush=True)
        url = f"https://huggingface.co/{item['repo']}/resolve/{item['revision']}/{item['file']}"
        subprocess.run([
            "curl", "--fail", "--location", "--retry", "5", "--retry-delay", "3",
            "--continue-at", "-", "--progress-bar", "--output", str(partial), url,
        ], check=True)
    if partial.stat().st_size != item["size"]:
        raise ValueError(f"Size mismatch: {partial}")
    digest = hashlib.sha256()
    with partial.open("rb") as file:
        for block in iter(lambda: file.read(8 * 1024 * 1024), b""):
            digest.update(block)
    if digest.hexdigest() != item["sha256"]:
        raise ValueError(f"Checksum mismatch: {partial}. Move the invalid file aside and retry.")
    if partial != path:
        partial.replace(path)
    print(f"Verified {path.name}", flush=True)


def main():
    items = json.loads(MANIFEST.read_text())
    print(f"Model packages: {sum(item['size'] for item in items) / 1e9:.1f} GB total.")
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(download_model, items))
    print("All models verified. Refresh Model Settings in the app.")


if __name__ == "__main__":
    main()
