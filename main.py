"""
MediaMorph — 多媒體檔案格式轉換工具

支援影像（JPG、PNG、HEIC、ICO）與影片（MP4、MOV、MKV）格式互轉，
提供拖曳上傳、批量處理、GPU 加速等功能。
"""

from converter.gui import create_app

if __name__ == "__main__":
    create_app()
