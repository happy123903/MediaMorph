"""Visual components for the MediaMorph desktop application."""

import os
import tkinter as tk
from tkinter import ttk

from .constants import IMAGE_FORMATS, VIDEO_FORMATS
from .optional import DND_FILES, HAS_DND

BACKGROUND = "#F3F6FB"
CARD = "#FFFFFF"
NAVY = "#14213B"
MUTED = "#687891"
BLUE = "#336BE6"
BORDER = "#DFE7F2"
FONT = "Microsoft JhengHei UI"


def _card(parent):
    return tk.Frame(
        parent, bg=CARD, padx=20, pady=10,
        highlightbackground=BORDER, highlightthickness=1,
    )


def _section_heading(parent, number, title):
    tk.Label(
        parent, text=f"{number}  /  {title}", bg=CARD, fg=NAVY,
        font=(FONT, 11, "bold"), anchor="w",
    ).pack(fill="x", pady=(0, 8))


class SectionsMixin:
    """Build the view and update its visible state."""

    def _build_ui(self):
        style = ttk.Style(self.root)
        if "clam" in style.theme_names():
            style.theme_use("clam")
        style.configure(
            "Media.TCombobox", padding=7, fieldbackground="#F8FAFE",
            background="#F8FAFE", foreground=NAVY,
        )
        style.map(
            "Media.TCombobox",
            fieldbackground=[("readonly", "#F8FAFE")],
            foreground=[("readonly", NAVY)],
        )
        style.configure(
            "Media.Horizontal.TProgressbar",
            troughcolor="#E8EEF8", background=BLUE, borderwidth=0, thickness=8,
        )

        header = tk.Frame(self.root, bg=NAVY, padx=28, pady=10)
        header.pack(fill="x")
        tk.Label(
            header, text="MediaMorph", bg=NAVY, fg="#FFFFFF",
            font=(FONT, 18, "bold"), anchor="w",
        ).pack(side="left")
        tk.Label(
            header, text="輕鬆轉換每一種格式", bg=NAVY, fg="#B9C9E7",
            font=(FONT, 10), anchor="e",
        ).pack(side="right")

        footer = tk.Frame(self.root, bg=BACKGROUND, padx=22, pady=8)
        footer.pack(side="bottom", fill="x")
        self._build_action_section(footer)

        viewport = tk.Frame(self.root, bg=BACKGROUND)
        viewport.pack(fill="both", expand=True)
        canvas = tk.Canvas(viewport, bg=BACKGROUND, highlightthickness=0)
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)
        body = tk.Frame(canvas, bg=BACKGROUND, padx=22, pady=8)
        window = canvas.create_window((0, 0), window=body, anchor="nw")

        def refresh_scroll():
            canvas.configure(scrollregion=canvas.bbox("all"))
            if body.winfo_reqheight() > canvas.winfo_height():
                if not scrollbar.winfo_ismapped():
                    scrollbar.pack(side="right", fill="y", before=canvas)
            elif scrollbar.winfo_ismapped():
                scrollbar.pack_forget()

        body.bind("<Configure>", lambda event: refresh_scroll())
        canvas.bind(
            "<Configure>",
            lambda event: (canvas.itemconfigure(window, width=event.width), refresh_scroll()),
        )
        canvas.bind_all(
            "<MouseWheel>",
            lambda event: canvas.yview_scroll(-int(event.delta / 120), "units"),
        )
        self._build_upload_section(body)
        self._build_output_section(body)
        self._build_format_section(body)

    def _build_upload_section(self, parent):
        self.upload_frame = _card(parent)
        self.upload_frame.pack(fill="x", pady=(0, 8))
        _section_heading(self.upload_frame, "01", "選擇檔案")
        self.drop_zone_default_bg = "#F7FAFF"
        self.upload_zone = tk.Frame(
            self.upload_frame, bg=self.drop_zone_default_bg,
            padx=18, pady=7, highlightbackground="#D9E3F2",
            highlightthickness=1,
        )
        self.upload_zone.pack(fill="x")
        self.upload_row = tk.Frame(self.upload_zone, bg=self.drop_zone_default_bg)
        self.upload_row.pack(fill="x")
        self.lbl_file_status = tk.Label(
            self.upload_row,
            text="尚未選擇檔案 · 可拖曳到這裡" if HAS_DND else "尚未選擇檔案",
            bg=self.drop_zone_default_bg,
            fg=MUTED, font=(FONT, 10), anchor="w",
        )
        self.lbl_file_status.pack(side="left", fill="x", expand=True)
        btn_upload = tk.Button(
            self.upload_row, text="選取檔案", command=self._on_upload,
            bg="#E8F0FF", fg="#245BC8", activebackground="#D9E7FF",
            activeforeground="#245BC8", font=(FONT, 9, "bold"),
            padx=15, pady=7, bd=0, relief="flat", cursor="hand2",
        )
        btn_upload.pack(side="right")
        if HAS_DND:
            for widget in (
                self.upload_frame, self.upload_zone, self.upload_row,
                self.lbl_file_status, btn_upload,
            ):
                widget.drop_target_register(DND_FILES)
                widget.dnd_bind("<<DropEnter>>", self._on_drop_enter)
                widget.dnd_bind("<<DropLeave>>", self._on_drop_leave)
                widget.dnd_bind("<<Drop>>", self._on_drop_files)

    def _build_output_section(self, parent):
        card = _card(parent)
        card.pack(fill="x", pady=(0, 8))
        _section_heading(card, "02", "儲存位置")
        row = tk.Frame(card, bg=CARD)
        row.pack(fill="x")
        path = tk.Entry(
            row, textvariable=self.output_dir, state="readonly",
            readonlybackground="#F8FAFE", fg="#465875",
            font=(FONT, 10), bd=0, relief="flat",
            highlightbackground=BORDER, highlightthickness=1,
        )
        path.pack(side="left", fill="x", expand=True, ipady=9)
        tk.Button(
            row, text="瀏覽資料夾", command=self._on_browse,
            bg="#E8F0FF", fg="#245BC8", activebackground="#D9E7FF",
            activeforeground="#245BC8", font=(FONT, 9, "bold"),
            padx=14, pady=8, bd=0, relief="flat", cursor="hand2",
        ).pack(side="left", padx=(9, 0))

    def _build_format_section(self, parent):
        card = _card(parent)
        card.pack(fill="x", pady=(0, 8))
        _section_heading(card, "03", "轉換設定")
        self.conversion_type = tk.StringVar(value="image")
        modes = tk.Frame(card, bg=CARD)
        modes.pack(fill="x", pady=(0, 7))
        self.mode_buttons = {}
        for label, value in (("影像", "image"), ("影片", "video")):
            button = tk.Button(
                modes, text=label, command=lambda mode=value: self._select_mode(mode),
                font=(FONT, 10, "bold"), bd=0, relief="flat", cursor="hand2",
                padx=24, pady=7,
            )
            button.pack(side="left", padx=(0, 7))
            self.mode_buttons[value] = button

        fields = tk.Frame(card, bg=CARD)
        fields.pack(fill="x")
        fields.columnconfigure(0, weight=1)
        fields.columnconfigure(1, weight=1)
        tk.Label(
            fields, text="來源格式", bg=CARD, fg=MUTED,
            font=(FONT, 9), anchor="w",
        ).grid(row=0, column=0, sticky="ew", padx=(0, 8), pady=(0, 5))
        tk.Label(
            fields, text="轉換為", bg=CARD, fg=MUTED,
            font=(FONT, 9), anchor="w",
        ).grid(row=0, column=1, sticky="ew", padx=(8, 0), pady=(0, 5))
        self.combo_source = ttk.Combobox(fields, state="readonly", style="Media.TCombobox")
        self.combo_source.grid(row=1, column=0, sticky="ew", padx=(0, 8))
        self.combo_target = ttk.Combobox(fields, state="readonly", style="Media.TCombobox")
        self.combo_target.grid(row=1, column=1, sticky="ew", padx=(8, 0))
        self._update_format_menus()

    def _build_action_section(self, parent):
        card = _card(parent)
        card.pack(fill="x")
        self.btn_convert = tk.Button(
            card, text="開始轉換", command=self._on_start_conversion,
            bg=BLUE, fg="#FFFFFF", activebackground="#245BC8",
            activeforeground="#FFFFFF", disabledforeground="#E5EBF7",
            font=(FONT, 11, "bold"), pady=8, bd=0, relief="flat",
            cursor="hand2",
        )
        self.btn_convert.pack(fill="x")
        self.progress_var = tk.DoubleVar(value=0)
        ttk.Progressbar(
            card, variable=self.progress_var, maximum=100,
            style="Media.Horizontal.TProgressbar",
        ).pack(fill="x", pady=(8, 0))
        self.lbl_progress = tk.Label(
            card, text="準備就緒", bg=CARD, fg=MUTED,
            font=(FONT, 9), anchor="w",
        )
        self.lbl_progress.pack(fill="x", pady=(4, 0))
        self.lbl_result = tk.Label(
            card, text="", bg=CARD, fg=MUTED,
            font=(FONT, 9), anchor="w", wraplength=650, justify="left",
        )

    def _select_mode(self, mode):
        self.conversion_type.set(mode)
        self._update_format_menus()

    def _refresh_file_status(self):
        self.lbl_file_status.config(bg=self.drop_zone_default_bg)
        if not self.selected_files:
            label = "尚未選擇檔案 · 可拖曳到這裡" if HAS_DND else "尚未選擇檔案"
            self.lbl_file_status.config(text=label, fg=MUTED)
            return
        count = len(self.selected_files)
        filename = os.path.basename(self.selected_files[0])
        label = filename if count == 1 else f"{filename}  等共 {count} 個檔案"
        self.lbl_file_status.config(text=label, fg=NAVY)

    def _update_format_menus(self):
        mode = self.conversion_type.get()
        options = IMAGE_FORMATS if mode == "image" else VIDEO_FORMATS
        for value, button in self.mode_buttons.items():
            active = value == mode
            button.config(
                bg=BLUE if active else "#EDF2FA",
                fg="#FFFFFF" if active else "#586A85",
                activebackground="#245BC8" if active else "#E3EBF7",
                activeforeground="#FFFFFF" if active else "#586A85",
            )
        self.combo_source["values"] = options
        self.combo_target["values"] = options
        if self.combo_source.get() not in options:
            self.combo_source.current(0)
        if self.combo_target.get() not in options:
            self.combo_target.current(1 if len(options) > 1 else 0)
