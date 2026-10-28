"""MediaMorph application controller."""

import os
import threading
import tkinter as tk
from tkinter import filedialog, messagebox

from .batch import BatchResult, plan_jobs, run_jobs
from .dependencies import install_command, missing_packages
from .gui_sections import SectionsMixin
from .logger import TkinterLogger
from .optional import HAS_DND, TkinterDnD
from .selection import detect_selection


class FormatConverterGUI(SectionsMixin):
    """Coordinate the widgets, file selection and background conversion."""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("MediaMorph")
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        width = min(680, screen_width - 60)
        height = min(600, screen_height - 130)
        self.root.geometry(
            f"{width}x{height}+{max(0, (screen_width - width) // 2)}+"
            f"{max(0, (screen_height - height) // 3)}"
        )
        self.root.minsize(min(560, width), min(480, height))
        self.root.configure(bg="#F3F6FB")

        # Use the same icon for the window and the packaged executable.
        icon_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.ico")
        if os.path.isfile(icon_path):
            try:
                self.root.iconbitmap(icon_path)
            except tk.TclError:
                pass

        self.selected_files: tuple[str, ...] = ()
        desktop = os.path.join(os.path.expanduser("~"), "Desktop")
        self.default_output_path = desktop if os.path.isdir(desktop) else os.path.expanduser("~")
        self.output_dir = tk.StringVar(value=self.default_output_path)
        self._build_ui()

    def _on_browse(self):
        folder = filedialog.askdirectory(title="選擇輸出資料夾", initialdir=self.output_dir.get())
        if folder:
            self.output_dir.set(folder)

    def _on_upload(self):
        files = filedialog.askopenfilenames(title="選擇要轉換的檔案")
        if files:
            self._handle_selected_files(tuple(files))

    def _on_drop_enter(self, event):
        self.upload_zone.config(bg="#E8F0FF", highlightbackground="#4177E9")
        self.upload_row.config(bg="#E8F0FF")
        self.lbl_file_status.config(text="放開滑鼠以加入檔案", fg="#245BC8", bg="#E8F0FF")

    def _on_drop_leave(self, event):
        self.upload_zone.config(bg=self.drop_zone_default_bg, highlightbackground="#D9E3F2")
        self.upload_row.config(bg=self.drop_zone_default_bg)
        self._refresh_file_status()

    def _on_drop_files(self, event):
        self._on_drop_leave(event)
        paths = self.root.tk.splitlist(event.data)
        files = tuple(path for path in paths if os.path.isfile(path))
        if any(os.path.isdir(path) for path in paths):
            messagebox.showwarning("略過資料夾", "拖曳的項目中含有資料夾，已自動略過，僅接受單一檔案。")
        if files:
            self._handle_selected_files(files)

    def _handle_selected_files(self, files: tuple[str, ...]):
        try:
            media_type, format_name = detect_selection(files)
        except ValueError as exc:
            messagebox.showerror("格式錯誤", str(exc))
            return
        self.selected_files = files
        self.conversion_type.set(media_type)
        self._update_format_menus()
        self.combo_source.set(format_name)
        self._refresh_file_status()

    def _on_start_conversion(self):
        if not self.selected_files:
            messagebox.showwarning("警告", "請先選擇至少一個檔案！")
            return
        media_type, source_format = detect_selection(self.selected_files)
        target_format = self.combo_target.get()
        if source_format == target_format:
            messagebox.showwarning("警告", "原始與目標格式相同，不需轉換！")
            return
        if source_format != self.combo_source.get():
            messagebox.showerror("格式錯誤", "原始格式與所選檔案不一致。")
            return
        if media_type != self.conversion_type.get():
            messagebox.showerror("格式錯誤", "所選檔案與轉換類型不一致。")
            return
        missing = missing_packages(media_type, self.selected_files, target_format)
        if missing:
            messagebox.showerror(
                "缺少轉檔套件",
                "目前啟動 MediaMorph 的 Python 缺少：" + "、".join(missing)
                + "\n\n請在終端機執行：\n" + install_command()
                + "\n\n安裝後重新啟動程式。",
            )
            return
        try:
            jobs = plan_jobs(self.selected_files, self.output_dir.get(), media_type, target_format)
        except ValueError as exc:
            messagebox.showerror("無法轉換", str(exc))
            return

        self.btn_convert.config(state="disabled", text="正在轉換…")
        self.progress_var.set(0)
        self.lbl_progress.config(text="正在準備轉換…", fg="#566781")
        self.lbl_result.config(text="")
        self.lbl_result.pack_forget()
        threading.Thread(target=self._run_conversion, args=(jobs,), daemon=True).start()

    def _run_conversion(self, jobs):
        def on_start(index, job):
            self.root.after(0, self.progress_var.set, 0)
            self.root.after(0, self.lbl_progress.config, {"text": f"正在轉換 ({index}/{len(jobs)}): {job.source.name}"})

        def make_logger(job):
            return TkinterLogger(self.root, self.progress_var, self.lbl_progress, job.source.name)

        result = run_jobs(jobs, on_start=on_start, logger_factory=make_logger)
        self.root.after(0, self._finish_conversion, result, str(jobs[0].destination.parent))

    def _finish_conversion(self, result: BatchResult, output_dir: str):
        self._reset_ui()
        self.progress_var.set(100)
        self.lbl_progress.config(text=f"完成 · {result.succeeded}/{result.total} 個檔案轉換成功", fg="#245BC8")
        if result.failures:
            self.lbl_result.config(text=f"{len(result.failures)} 個檔案失敗，詳情見提示視窗。", fg="#B45309")
            self.lbl_result.pack(fill="x")
            messagebox.showwarning("部分檔案轉換失敗", "\n".join(result.failures))
        else:
            self.lbl_result.config(text=f"輸出位置：{output_dir}", fg="#52627C")
            self.lbl_result.pack(fill="x")

    def _reset_ui(self):
        self.btn_convert.config(state="normal", text="開始轉換")


def create_app():
    """Build and start the desktop application."""
    root = TkinterDnD.Tk() if HAS_DND else tk.Tk()
    FormatConverterGUI(root)
    root.mainloop()
