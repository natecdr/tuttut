import logging
import os
from pathlib import Path

import eel

from tuttut.GUI import config, gui_utils, dialogs, generate

class UIOpenMode:
    NONE = 0
    CHROME = 1
    USER_DEFAULT = 2

# Setup eels root folder
eel.init(config.FRONTEND_ASSET_FOLDER)

def __setup_logging_ui_forwarding():
    module_logger = logging.getLogger('web_gui')
    handler = logging.StreamHandler(gui_utils.ForwardToFunctionStream(print_ui))
    handler.setFormatter(logging.Formatter('%(message)s'))
    module_logger.addHandler(handler)

@eel.expose
def initialise():
    """Initialisation du logging."""
    __setup_logging_ui_forwarding()

@eel.expose
def open_folder_in_explorer(path):
    """ Ouvre un fichier dans l'explorateur de fichiers. """
    if not gui_utils.open_output_folder(path):
        pass  # TODO Send message saying this failed

@eel.expose
def ask_file():
    """ Demande un/des fichiers à l'utilisateur."""
    file = dialogs.ask_file()
    return file

@eel.expose
def ask_folder():
    """ Demande un dossier à l'utilisateur. """
    return dialogs.ask_folder()

@eel.expose
def does_file_exist(file_path):
    """ Vérifie si un fichier existe. """
    return os.path.isfile(file_path)

@eel.expose
def does_folder_exist(path):
    """ Vérifie si un dossier existe. """
    return os.path.isdir(path)

@eel.expose
def get_files_in_folder(path):
    """ Retourne les fichiers présents dans un dossier. """
    paths = [str(Path(path, filename)) for filename in os.listdir(path)]
    paths = gui_utils.format_paths(paths)
    return paths

@eel.expose
def tabify(path, output_folder, parameters):
    """Lance le nettoyage.

    Args:
        paths (str[]): Chemins des fichiers à nettoyer
        output_folder (str): Chemin du dossier de sortie
        preset (Dict): Paramètres de nettoyage
    """
    generate.tabify(path, output_folder, parameters)

    print_ui('Complete.\n')
    eel.signalProcessingComplete(True)()

def print_ui(message):
    """ Ecrit un message dans la console. """
    eel.putMessageInOutput(message)()

def color_list_element(element_id, color):
    """ Ajoute un indicateur coloré à un élément de la liste de scans."""
    eel.colorListElement(element_id, color)

def is_halted():
    """ Vérifie si le nettoyage a été interrompu """
    return eel.isHalted()()

def start(open_mode):
    """ Start the UI using Eel """
    try:
        chrome_available = gui_utils.can_use_chrome()
        if open_mode == UIOpenMode.CHROME and chrome_available:
            eel.start('index.html', size=(650, 250), port=0)
        elif open_mode == UIOpenMode.USER_DEFAULT or (open_mode == UIOpenMode.CHROME and not chrome_available):
            eel.start('index.html', size=(650, 250), port=0, mode='user default')
        else:
            port = gui_utils.get_port()
            print('Server starting at http://localhost:' + str(port) + '/index.html')
            eel.start('index.html', size=(650, 250), host='localhost', port=port, mode=None, close_callback=lambda x, y: None)
    except (SystemExit, KeyboardInterrupt):
        pass  # This is what the bottle server raises

if __name__ == "__main__":
    start(UIOpenMode.CHROME)