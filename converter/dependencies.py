"""Check conversion dependencies in the Python running the application."""

import importlib.util
import sys
from pathlib import Path


def missing_packages(media_type: str, files: tuple[str, ...], target_format: str) -> tuple[str, ...]:
    if media_type == "image":
        modules = {"PIL": "Pillow"}
        heif_input = any(Path(file).suffix.lower() in (".heic", ".heif") for file in files)
        if heif_input or target_format == "HEIC / HEIF":
            modules["pillow_heif"] = "pillow-heif"
    else:
        modules = {"moviepy": "moviepy", "proglog": "proglog"}
    return tuple(package for module, package in modules.items() if importlib.util.find_spec(module) is None)


def install_command() -> str:
    """Use this exact interpreter so packages land in the running environment."""
    requirements = Path(__file__).resolve().parent.parent / "requirements.txt"
    return f'"{sys.executable}" -m pip install -r "{requirements}"'
