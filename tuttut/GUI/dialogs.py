def _tk_root():
    try:
        from tkinter import Tk
    except ImportError as e:
        raise RuntimeError(
            "tkinter is not installed. Linux: sudo apt install python3-tk. "
            "Windows/macOS: install Python from python.org"
        ) from e
        
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    return root

def ask_file():
    root = _tk_root()
    from tkinter.filedialog import askopenfilename
    
    try:
        path = askopenfilename(parent=root, filetypes=[("MIDI files", "*.mid *.midi"), ("All files", "*.*")])
    finally:
        root.destroy()
        
    return path or None


def ask_folder():
    root = _tk_root()
    from tkinter.filedialog import askdirectory
    try:
        folder = askdirectory(parent=root)
    finally:
        root.destroy()
    return folder or None