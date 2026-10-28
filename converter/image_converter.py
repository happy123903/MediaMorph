"""
converter/image_converter.py
影像格式轉換引擎
"""

from pathlib import Path

from PIL import Image

from .constants import ICO_SIZES


def convert_image(file_path: str, out_path: str, target_ext: str) -> None:
    """將單一影像檔轉換為指定格式。

    Parameters
    ----------
    file_path : str
        來源影像的絕對路徑。
    out_path : str
        輸出影像的絕對路徑。
    target_ext : str
        目標副檔名，例如 ``'.jpg'``、``'.png'``、``'.ico'``。

    Raises
    ------
    Exception
        當 Pillow 無法開啟或儲存檔案時，由上層呼叫者負責捕捉。
    """
    if Path(file_path).suffix.lower() in (".heic", ".heif") or target_ext == ".heic":
        import pillow_heif

        pillow_heif.register_heif_opener()

    with Image.open(file_path) as source:
        image = source.copy()

    # Transparent pixels need a visible background in formats without alpha.
    if target_ext in (".jpg", ".heic"):
        if image.mode in ("RGBA", "LA") or "transparency" in image.info:
            rgba = image.convert("RGBA")
            background = Image.new("RGB", rgba.size, "white")
            background.paste(rgba, mask=rgba.getchannel("A"))
            image = background
        elif image.mode != "RGB":
            image = image.convert("RGB")

    if target_ext == ".ico":
        image.save(out_path, format="ICO", sizes=ICO_SIZES)
    else:
        image.save(out_path)
