import logging
import os
from pathlib import Path
import traceback

import eel

from tuttut.GUI import config, gui_utils, dialogs, generate

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
    try:
        return dialogs.ask_file()
    except RuntimeError as e:
        print_ui(str(e))
        return None

@eel.expose
def ask_folder():
    try:
        return dialogs.ask_folder()
    except RuntimeError as e:
        print_ui(str(e))
        return None

@eel.expose
def does_file_exist(file_path):
    return os.path.isfile(file_path)

@eel.expose
def does_folder_exist(path):
    return os.path.isdir(path)

@eel.expose
def get_files_in_folder(path):
    paths = [str(Path(path, filename)) for filename in os.listdir(path)]
    paths = gui_utils.format_paths(paths)
    return paths

@eel.expose
def tabify(path, output_folder, parameters):
    try:
        generate.tabify(path, output_folder, parameters)
    except Exception as e:
        traceback.print_exc()
        print_ui(f"Error: {e}. The tool can struggle with complex multi-channel MIDI files.")
        eel.signalProcessingComplete(False)()
        return

    print_ui('Complete.\n')
    eel.signalProcessingComplete(True)()

def print_ui(message):
    """ Prints a message in the console. """
    eel.putMessageInOutput(message)()

def color_list_element(element_id, color):
    eel.colorListElement(element_id, color)

def is_halted():
    return eel.isHalted()()

def start(open_mode):
    """ Start the UI using Eel """
    try:
        chrome_available = gui_utils.can_use_chrome()
        if open_mode == config.UIOpenMode.CHROME and chrome_available:
            eel.start('index.html', size=(650, 250), port=0)
        elif open_mode == config.UIOpenMode.USER_DEFAULT or (open_mode == config.UIOpenMode.CHROME and not chrome_available):
            eel.start('index.html', size=(650, 250), port=0, mode='user default')
        else:
            port = gui_utils.get_port()
            print('Server starting at http://localhost:' + str(port) + '/index.html')
            eel.start('index.html', size=(650, 250), host='localhost', port=port, mode=None, close_callback=lambda x, y: None)
    except (SystemExit, KeyboardInterrupt):
        pass  # This is what the bottle server raises

if __name__ == "__main__":
    start(config.UIOpenMode.CHROME)