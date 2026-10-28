# MediaMorph

MediaMorph 是桌面影像與影片格式轉換工具，支援單檔及同格式批次轉換。

## 功能

- 影像：JPG/JPEG、PNG、HEIC/HEIF、ICO。ICO 輸出包含多種圖示尺寸。
- 影片：MP4、MOV、MKV。轉為 MP4 時依序嘗試 NVIDIA、AMD、Intel 硬體編碼器，最後使用軟體編碼。
- 選檔時自動辨識格式，也支援拖曳檔案。
- 輸出檔名使用 `_converted` 後綴；遇到同名檔案時加上流水號，避免覆寫。
- 轉換在背景執行，逐檔顯示結果與失敗原因。
- 透明影像轉為 JPG/HEIC 時，以白色填滿透明區域。

## 轉檔技術

| 技術 | 用途 |
| --- | --- |
| Pillow | 讀取、處理及儲存 JPG、PNG、ICO 等影像格式；轉換透明影像時處理背景色。 |
| pillow-heif | 為 Pillow 提供 HEIC/HEIF 的讀寫能力。 |
| MoviePy | 載入影片、處理音訊與影格，並管理轉檔流程。 |
| FFmpeg | 實際執行影片與音訊編碼；MP4 會優先嘗試 NVIDIA NVENC、AMD AMF、Intel Quick Sync，最後回退至 `libx264`。 |
| proglog | 將影片處理進度回報至介面。 |

硬體編碼是否可用，取決於電腦的顯示卡、驅動程式與 FFmpeg 支援情況。

## 環境與啟動

建議使用 Windows 和 Python 3.10 以上版本。啟動入口為 `main.py`：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python main.py
```

## 程式架構

`main.py` 啟動桌面介面。選檔後，`selection.py` 確認來源格式，`dependencies.py` 檢查轉檔套件，`batch.py` 為每個檔案規劃不覆寫既有檔案的輸出路徑，再由影像或影片轉換模組執行；`logger.py` 負責回報影片進度。

新增格式時，先更新 `constants.py` 的格式與副檔名對照，再於對應的轉換模組加入處理邏輯。

## 專案結構

```text
MediaMorph/
├── main.py                    # 桌面程式入口
├── converter/
│   ├── constants.py           # 格式與編碼器設定
│   ├── selection.py           # 選檔格式驗證
│   ├── dependencies.py        # 轉檔套件檢查
│   ├── batch.py               # 批次任務規劃與執行
│   ├── image_converter.py     # 影像轉換
│   ├── video_converter.py     # 影片轉換
│   ├── logger.py              # 影片進度回報
│   ├── optional.py            # 可選的拖曳功能
│   ├── gui_sections.py        # 畫面元件
│   └── gui.py                 # GUI 事件與流程控制
└── requirements.txt
```

