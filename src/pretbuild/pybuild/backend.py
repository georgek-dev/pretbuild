import os
import io
import tarfile
import zipfile
try:
    import tomllib # novm
except ModuleNotFoundError:
    import tomli as tomllib
import base64
import hashlib

def _metadata():
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    toml = os.path.join(root, "pyproject.toml")

    with open(toml, "rb") as f:
        data = tomllib.load(f)

    info = data.get("project", {})
    name = info.get("name", "package").replace("-", "_")
    version = info.get("version", "0.0.0")

    return name, version, root

def _generate_metadata(name, version):
    metadata = f"Metadata-Version: 2.4\nName: {name}\nVersion: {version}"
    wheel = "Wheel-Version: 1.0\nGenerator: pretbuild (0.1.0)\nRoot-Is-Purelib: true\nTag: py3-none-any"

    return metadata, wheel

def _collect(src):
    files = []
    if os.path.exists(src):
        for base, _, names in os.walk(src):
            for fname in names:
                if fname.endswith((".pyc", ".pyo")) or "__pycache__" in base:
                    continue
                files.append(os.path.join(base, fname))
    return files

def _tick(progress, done, count, name):
    if progress:
        progress(done, count, name)

def prepare_metadata_for_build_wheel(metadata_directory, config_settings=None):
    name, version, _ = _metadata()
    distinfo = os.path.join(metadata_directory, f"{name}-{version}.dist-info")
    os.makedirs(distinfo, exist_ok=True)
    md, winfo = _generate_metadata(name, version)
    with open(os.path.join(distinfo, "METADATA"), "w", encoding="UTF-8") as f:
        f.write(md)
    with open(os.path.join(distinfo, "WHEEL"), "w", encoding="UTF-8") as f:
        f.write(winfo)

    return f"{name}-{version}.dist-info"

def get_requires_for_build_sdist(config_settings=None):
    return []

def get_requires_for_build_wheel(config_settings=None):
    return []

def get_requires_for_build_editable(config_settings=None):
    return []

def build_editable(wheel_directory, config_settings=None, metadata_directory=None, progress=None):
    name, version, root = _metadata()
    file = f"{name}-{version}-py3-none-any.whl"
    path = os.path.join(wheel_directory, file)
    prefix = f"{name}-{version}.dist-info"
    abspath = os.path.abspath(os.path.join(root, "src"))
    entries = []
    count = 4
    done = 0

    def add(zip, filbytes, arc):
        nonlocal done
        zip.writestr(arc, filbytes)
        sha256 = hashlib.sha256(filbytes).digest()
        b64 = base64.urlsafe_b64encode(sha256).decode("utf-8").rstrip('=')
        entries.append(f"{arc},sha256={b64},{len(filbytes)}")
        done += 1
        _tick(progress, done, count, arc)

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as f:
        md, winfo = _generate_metadata(name, version)
        add(f, md.encode("utf-8"), f"{prefix}/METADATA")
        add(f, winfo.encode("utf-8"), f"{prefix}/WHEEL")
        pth = f"{abspath}\n"
        add(f, pth.encode("utf-8"), f"{name}.pth")
        rpath = f"{prefix}/RECORD"
        entries.append(f"{rpath},,")
        f.writestr(rpath, "\n".join(entries) + "\n")
        done += 1
        _tick(progress, done, count, rpath)

    return file

def build_wheel(wheel_directory, config_settings=None, metadata_directory=None, progress=None):
    name, version, root = _metadata()
    file = f"{name}-{version}-py3-none-any.whl"
    wpath = os.path.join(wheel_directory, file)
    src = os.path.join(root, "src")
    prefix = f"{name}-{version}.dist-info"
    entries = []
    files = _collect(src)
    count = len(files) + 3
    done = 0

    def add(zip, filbytes, arc):
        nonlocal done
        zip.writestr(arc, filbytes)
        sha256 = hashlib.sha256(filbytes).digest()
        b64 = base64.urlsafe_b64encode(sha256).decode("utf-8").rstrip('=')
        entries.append(f"{arc},sha256={b64},{len(filbytes)}")
        done += 1
        _tick(progress, done, count, arc)

    with zipfile.ZipFile(wpath, "w", zipfile.ZIP_DEFLATED) as f:
        md, winfo = _generate_metadata(name, version)
        add(f, md.encode("utf-8"), f"{prefix}/METADATA")
        add(f, winfo.encode("utf-8"), f"{prefix}/WHEEL")

        for fpath in files:
            apath = os.path.relpath(fpath, src).replace(os.sep, "/")

            with open(fpath, "rb") as fp:
                c = fp.read()
            add(f, c, apath)

        record = f"{prefix}/RECORD"
        entries.append(f"{record},,")
        f.writestr(record, "\n".join(entries) + "\n")
        done += 1
        _tick(progress, done, count, record)

    return file

def build_sdist(sdist_directory, config_settings=None, progress=None):
    name, version, root = _metadata()
    file = f"{name}-{version}.tar.gz"
    path = os.path.join(sdist_directory, file)
    pyproject = os.path.join(root, "pyproject.toml")
    src = os.path.join(root, "src")
    files = [pyproject] + _collect(src)
    count = len(files) + 1
    done = 0
    md, _ = _generate_metadata(name, version)

    with tarfile.open(path, "w:gz") as f:
        pkginfo = f"{name}-{version}/PKG-INFO"
        data = md.encode("utf-8")
        member = tarfile.TarInfo(pkginfo)
        member.size = len(data)
        f.addfile(member, io.BytesIO(data))
        done += 1
        _tick(progress, done, count, pkginfo)

        for fpath in files:
            arc = f"{name}-{version}/" + os.path.relpath(fpath, root).replace(os.sep, "/")
            f.add(fpath, arcname=arc)
            done += 1
            _tick(progress, done, count, arc)

    return file
