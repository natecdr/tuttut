from __future__ import print_function
import io
import os
from pathlib import Path
import platform
import socket

from eel import chrome

class ForwardToFunctionStream(io.TextIOBase):
    def __init__(self, output_function=print):
        self.output_function = output_function

    def write(self, string):
        self.output_function(string)
        return len(string)

def can_use_chrome():
    """ Vérifie si on peut utiliser chrome pour l'interface """
    chrome_instance_path = chrome.find_path()
    return chrome_instance_path is not None and os.path.exists(chrome_instance_path)


def open_output_folder(folder):
    """ Ouvre un dossier dans l'explorateur de fichiers local """
    folder_directory = os.path.abspath(folder)
    if platform.system() == 'Windows':
        os.startfile(folder_directory, 'explore')
    elif platform.system() == 'Linux':
        os.system('xdg-open "' + folder_directory + '"')
    elif platform.system() == 'Darwin':
        os.system('open "' + folder_directory + '"')
    else:
        return False
    return True

def format_paths(paths):
    """ Formatte les chemins de fichiers. """
    paths = [str(Path(os.sep, path)) for path in paths]
    return paths

def get_port():
    """ Get an available port by starting a new server, stopping and and returning the port """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 0))
    port = sock.getsockname()[1]
    sock.close()
    return port