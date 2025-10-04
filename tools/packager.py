import zipfile
import os
import tempfile
import requests
import shutil
import sys
import subprocess
from tqdm import tqdm

python_url = "https://www.python.org/ftp/python/3.10.0/python-3.10.0-embed-amd64.zip"
get_pip_url = "https://bootstrap.pypa.io/get-pip.py"

include = {
    "bin",
    "examples",
    "src",
    "LICENSE.md",
    "CHANGELOG.md",
    "README.md",
    "SECURITY.md",
    "requirements.txt",
    "packages"
}

ms_build = r"C:\Program Files\Microsoft Visual Studio\2022\Community\MSBuild\Current\Bin\amd64\MSBuild.exe"
installer_windows_path = "../installer/windows"

version = sys.argv[1] if len(sys.argv) > 1 else None
if version is None:
    raise Exception("Missing argument.")

version_short = ".".join(version.split(".")[:-1]) if "." in version else version

output_zip = f"mrya-{version}.zip"
output_installer = f"mrya-installer-{version}.exe"

# ---- MAIN LOGIC ----
tmpdir = tempfile.mkdtemp()
python_zip = os.path.join(tmpdir, "python.zip")
python_dir = os.path.join(tmpdir, "python")

def download_with_progress(url, path, desc):
    r = requests.get(url, stream=True)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    with open(path, "wb") as f, tqdm(
        total=total, unit="B", unit_scale=True, desc=desc
    ) as bar:
        for chunk in r.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                bar.update(len(chunk))

print("Downloading Python embed package...")
download_with_progress(python_url, python_zip, "Python Embed")

print("Extracting Python embed package...")
with zipfile.ZipFile(python_zip, "r") as zf:
    members = zf.infolist()
    for member in tqdm(members, desc="Extracting Python", unit="file"):
        zf.extract(member, python_dir)

# --- Enable site packages ---
pth_files = [f for f in os.listdir(python_dir) if f.endswith("._pth")]
if pth_files:
    pth_path = os.path.join(python_dir, pth_files[0])
    print(f"Enabling site-packages in {pth_path}")
    with open(pth_path, "r", encoding="utf-8") as f:
        content = f.read().replace("#import site", "import site")
    with open(pth_path, "w", encoding="utf-8") as f:
        f.write(content)

# --- Install pip ---
get_pip_path = os.path.join(tmpdir, "get-pip.py")
print("Downloading get-pip.py...")
download_with_progress(get_pip_url, get_pip_path, "get-pip.py")

print("Installing pip into embedded Python...")
subprocess.run([os.path.join(python_dir, "python.exe"), get_pip_path, "--no-warn-script-location"], check=True)

# --- Install pygame ---
print("Installing pygame into embedded Python...")
subprocess.run([os.path.join(python_dir, "python.exe"), "-m", "pip", "install", "--no-cache-dir", "pygame"], check=True)

# --- Clean pip caches ---
pip_cache = os.path.join(python_dir, "Lib", "site-packages", "pip")
if os.path.exists(pip_cache):
    shutil.rmtree(pip_cache, ignore_errors=True)

# --- Pack ZIP ---
print("Packing into final zip...")
with zipfile.ZipFile(output_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    # 1. Pack Python embed (with pygame)
    all_files = []
    for root, _, files in os.walk(python_dir):
        for file in files:
            abs_path = os.path.join(root, file)
            rel_path = os.path.relpath(abs_path, tmpdir)
            all_files.append((abs_path, rel_path))
    for abs_path, rel_path in tqdm(all_files, desc="Packing Python", unit="file"):
        zf.write(abs_path, rel_path)

    # 2. Pack project files
    for item in include:
        path = os.path.join("..", item)
        if not os.path.exists(path):
            continue

        if os.path.isdir(path):
            all_files = []
            for root, _, files in os.walk(path):
                for file in files:
                    abs_path = os.path.join(root, file)
                    rel_path = os.path.relpath(abs_path, "..")
                    all_files.append((abs_path, rel_path))
            for abs_path, rel_path in tqdm(all_files, desc=f"Packing {item}", unit="file"):
                zf.write(abs_path, rel_path)

                # Handle special case for bin files
                if "bin" in rel_path.split(os.sep):
                    name, ext = os.path.splitext(os.path.basename(file))
                    versioned_rel = os.path.join(
                        os.path.dirname(rel_path),
                        f"{name}{version_short}{ext}"
                    )
                    zf.write(abs_path, versioned_rel)
        else:
            rel_path = os.path.relpath(path, "..")
            tqdm.write(f"Packing {item}...")
            zf.write(path, rel_path)

print(f"Created {output_zip}")

# Cleanup temp dir
shutil.rmtree(tmpdir)

print("Building release windows build...")
subprocess.run([
    ms_build,
    f"{installer_windows_path}\\windows.sln",
    "/p:Configuration=Release",
    "/p:Platform=x64"
], check=True)

print("To generate EXE run")

# Find built .exe (assuming Release folder)
built_exe = os.path.join(installer_windows_path, "x64", "Release", "windows.exe")
if not os.path.exists(built_exe):
    raise FileNotFoundError(f"Cannot find built installer at {built_exe}")

if os.path.exists(output_installer):
    os.remove(output_installer)

print(f"copy /b {built_exe.replace('/', '\\')} + {output_zip.replace('/', '\\')} {output_installer.replace('/', '\\')}")
