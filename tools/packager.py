import zipfile
import os
import tempfile
import requests
import shutil
import sys

python_url = "https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-amd64.zip"
include = {
    "bin",
    "examples",
    "src",
    "LICENSE.md",
    "CHANGELOG.md",
    "README.md",
    "SECURITY.md",
    "requirements.txt",
}

version = sys.argv[1] if len(sys.argv) > 1 else "0.0.0"

output_zip = f"mrya-{version}.zip"

# Create temp directory
tmpdir = tempfile.mkdtemp()
python_zip = os.path.join(tmpdir, "python.zip")

print("Downloading Python embed package...")
r = requests.get(python_url, stream=True)
r.raise_for_status()
with open(python_zip, "wb") as f:
    for chunk in r.iter_content(chunk_size=8192):
        f.write(chunk)

print("Extracting Python embed package...")
with zipfile.ZipFile(python_zip, "r") as zf:
    zf.extractall(os.path.join(tmpdir, "python"))

with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    # 1. Pack Python embed
    for root, dirs, files in os.walk(os.path.join(tmpdir, "python")):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, tmpdir)  # keep structure under tmp
            print(f"Packing Python: {rel_path}")
            zf.write(abs_path, rel_path)

    # 2. Pack project files
    for item in os.listdir(".."):
        if item in include:
            path = os.path.join("..", item)
            print(f"Packing {item}...")

            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for file in files:
                        abs_path = os.path.join(root, file)
                        rel_path = os.path.relpath(abs_path, "..")
                        zf.write(abs_path, rel_path)
            else:
                rel_path = os.path.relpath(path, "..")
                zf.write(path, rel_path)

print(f"Created {output_zip}")

# Cleanup temp dir
shutil.rmtree(tmpdir)
