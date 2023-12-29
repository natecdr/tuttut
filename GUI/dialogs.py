import platform
import sys
try:
    from tkinter import Tk
except ImportError:
    try:
        from Tkinter import Tk
    except ImportError:
        # If no versions of tkinter exist (most likely linux) provide a message
        if sys.version_info.major < 3:
            print("Error: Tkinter not found")
            print('For linux, you can install Tkinter by executing: "sudo apt-get install python-tk"')
            sys.exit(1)
        else:
            print("Error: tkinter not found")
            print('For linux, you can install tkinter by executing: "sudo apt-get install python3-tk"')
            sys.exit(1)
try:
    from tkinter.filedialog import askopenfilename, askdirectory, askopenfilenames, asksaveasfilename
except ImportError:
    from tkFileDialog import askopenfilename, askdirectory, askopenfilenames, asksaveasfilename

def ask_file():
    """ Demande un ou des fichiers à l'utilisateur """
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    file_path = askopenfilename(parent=root)
    root.update()

    return file_path if bool(file_path) else None

def ask_folder():
    """ Demande un dossier à l'utilisateur """
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)
    folder = askdirectory(parent=root)
    root.update()

    return folder if bool(folder) else None