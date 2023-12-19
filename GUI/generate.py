import sys
import os
import pretty_midi
from pathlib import Path

sys.path.append("./..")

import os
import shutil
import traceback

from GUI import gui

from tuttut.tab import Tab
from tuttut.theory import Tuning

def tabify(midi_path, output_dir): 
    """Nettoie de A à Z un scan.

    Args:
        path (str): Chemin du scan
        output_path (str): Chemin de sortie du scan
        preset (Dict): Paramètres de nettoyage
    """
    
    weights = {'b': 1, 'height': 1, 'length': 1, 'n_changed_strings': 1}

    filepath = Path(midi_path)
    f = pretty_midi.PrettyMIDI(filepath.as_posix())
    tab = Tab(filepath.stem, Tuning(), f, weights=weights, output_dir = output_dir)
    # tab = Tab(file.stem, Tuning([Note(69), Note(64), Note(60), Note(67)]), f, weights=weights)
    tab.to_ascii()
    tab.to_json()
