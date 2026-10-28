"""Validation and format detection for selected files."""

from pathlib import Path

from .constants import EXT_MAP


def detect_selection(files: tuple[str, ...]) -> tuple[str, str]:
    """Return (media type, display format) for a homogeneous file selection."""
    if not files:
        raise ValueError("請先選擇至少一個檔案。")

    extensions = {Path(path).suffix.lower() for path in files}
    if len(extensions) != 1:
        raise ValueError("批量上傳時，所有檔案必須是相同的格式。")

    extension = extensions.pop()
    if extension not in EXT_MAP:
        raise ValueError(f"不支援的副檔名：{extension or '（無副檔名）'}")
    return EXT_MAP[extension]
