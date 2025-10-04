import zipfile
import os
import tempfile
import requests
import shutil
import sys
import subprocess


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

ms_build = r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\amd64\MSBuild.exe" # hacky!
installer_windows_path = "../installer/windows"

version = sys.argv[1] if len(sys.argv) > 1 else None

if version == None:
    raise Exception("Missing argument.")

output_zip = f"mrya-{version}.zip"
output_installer = f"mrya-installer-{version}.exe"

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

print("Building release windows build")

subprocess.run([
    ms_build,
    f"{installer_windows_path}\\windows.sln",
    "/p:Configuration=Release",
    "/p:Platform=x64"
], check=True)

print("Generating finished exe")

# Find built .exe (assuming Release folder)
built_exe = os.path.join(installer_windows_path, "x64", "Release", "windows.exe")
if not os.path.exists(built_exe):
    raise FileNotFoundError(f"Cannot find built installer at {built_exe}")

print("Combining installer and zip into single EXE...")

if os.path.exists(output_installer):
    os.remove(output_installer)

os.system(f"copy /b {built_exe.replace("/", "\\")} + {output_zip.replace("/", "\\")} {output_installer.replace("/", "\\")}")

print(f"Combined installer created: {output_installer}")