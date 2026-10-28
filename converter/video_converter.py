"""
converter/video_converter.py
影片格式轉換引擎
"""

from moviepy import VideoFileClip

from .constants import MP4_CODECS


def convert_video(file_path: str, out_path: str, target_ext: str, logger=None) -> None:
    """將單一影片檔轉換為指定格式。

    對於 MP4 目標格式，會依序嘗試 GPU 硬體加速編碼器，
    全部失敗後才回退至軟體編碼器 (libx264)。

    Parameters
    ----------
    file_path : str
        來源影片的絕對路徑。
    out_path : str
        輸出影片的絕對路徑。
    target_ext : str
        目標副檔名，例如 ``'.mp4'``、``'.mov'``、``'.mkv'``。
    logger : ProgressBarLogger | None
        moviepy 進度記錄器（通常為 ``TkinterLogger`` 實例）。

    Raises
    ------
    RuntimeError
        當所有編碼器都無法成功轉換時拋出。
    """
    clip = VideoFileClip(file_path)

    try:
        if target_ext == ".mp4":
            _convert_mp4_with_fallback(clip, out_path, logger)
        else:
            clip.write_videofile(out_path, logger=logger)
    finally:
        clip.close()


def _convert_mp4_with_fallback(clip, out_path: str, logger) -> None:
    """嘗試多種 H.264 編碼器，優先使用硬體加速。"""
    for codec in MP4_CODECS:
        try:
            clip.write_videofile(out_path, codec=codec, audio_codec="aac", logger=logger)
            return  # 成功即返回
        except Exception:
            print(f"後台日誌 - {codec} 失敗，準備嘗試下一個。")
            continue

    raise RuntimeError("所有硬體與軟體編碼器皆失效。")
