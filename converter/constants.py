"""
converter/constants.py
格式常數與設定集中管理
"""

# ─── 支援的格式清單 ────────────────────────────────────────────
IMAGE_FORMATS = ["JPG / JPEG", "PNG", "HEIC / HEIF", "ICO"]
VIDEO_FORMATS = ["MP4", "MOV", "MKV"]

# ─── 副檔名 → (類型, 格式顯示名稱) ──────────────────────────
EXT_MAP = {
    ".jpg":  ("image", "JPG / JPEG"),
    ".jpeg": ("image", "JPG / JPEG"),
    ".png":  ("image", "PNG"),
    ".heic": ("image", "HEIC / HEIF"),
    ".heif": ("image", "HEIC / HEIF"),
    ".ico":  ("image", "ICO"),
    ".mp4":  ("video", "MP4"),
    ".mov":  ("video", "MOV"),
    ".mkv":  ("video", "MKV"),
}

# ─── 格式顯示名稱 → 目標副檔名 ──────────────────────────────
TARGET_EXT_MAP = {
    "JPG / JPEG":  ".jpg",
    "PNG":         ".png",
    "HEIC / HEIF": ".heic",
    "ICO":         ".ico",
    "MP4":         ".mp4",
    "MOV":         ".mov",
    "MKV":         ".mkv",
}

# ─── ICO 多尺寸打包規格 ──────────────────────────────────────
ICO_SIZES = [
    (256, 256),
    (128, 128),
    (64, 64),
    (48, 48),
    (32, 32),
    (16, 16),
]

# ─── 影片 MP4 編碼器回退清單（優先使用 GPU 硬體加速）────────
MP4_CODECS = [
    "h264_nvenc",   # NVIDIA GPU
    "h264_amf",     # AMD GPU
    "h264_qsv",     # Intel Quick Sync
    "libx264",      # 軟體編碼（保底）
]
