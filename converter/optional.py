"""Optional GUI integration for drag and drop."""

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None

HAS_DND = TkinterDnD is not None
