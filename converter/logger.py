"""
converter/logger.py
自訂進度記錄器 — 將 moviepy 轉換進度即時回報至 Tkinter GUI
"""

# 匯入 proglog（若失敗則提供空殼基底類別，避免啟動階段崩潰）
try:
    from proglog import ProgressBarLogger
except ImportError:
    class ProgressBarLogger:
        """proglog 未安裝時的空殼替代品"""
        pass


class TkinterLogger(ProgressBarLogger):
    """將 moviepy 的 bars_callback 轉譯為 Tkinter 進度條更新。

    Parameters
    ----------
    root : tk.Tk
        Tkinter 主視窗，用於 thread-safe 的 ``after()`` 排程。
    progress_var : tk.DoubleVar
        綁定到 ``ttk.Progressbar`` 的變數。
    lbl_progress : tk.Label
        顯示目前轉換狀態的文字標籤。
    current_filename : str
        正在轉換的檔案名稱，用於進度文字。
    """

    def __init__(self, root, progress_var, lbl_progress, current_filename):
        super().__init__()
        self.root = root
        self.progress_var = progress_var
        self.lbl_progress = lbl_progress
        self.current_filename = current_filename

    def bars_callback(self, bar, attr, value, old_value=None):
        total = self.bars.get(bar, {}).get("total")
        if total:
            percentage = (value / total) * 100

            # 自動判斷階段：影像處理 (frames/t) 總數通常較多
            stage_name = (
                "處理影像中" if bar in ("t", "frames") or total > 1000 else "處理音訊中"
            )

            self.root.after(0, self.progress_var.set, percentage)
            self.root.after(
                0,
                lambda stage=stage_name, pct=int(percentage): self.lbl_progress.config(
                    text=f"正在轉換 {self.current_filename} - {stage} ({pct}%)"
                ),
            )
