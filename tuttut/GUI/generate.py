import sys
import os
import pretty_midi
from pathlib import Path

sys.path.append("./..")

import os

from tuttut.logic.tab import Tab
from tuttut.logic.theory import Tuning

def tabify(midi_path, output_dir, parameters): 
    """Nettoie de A à Z un scan.

    Args:
        path (str): Chemin du scan
        output_path (str): Chemin de sortie du scan
        preset (Dict): Paramètres de nettoyage
    """
    
    weights = {'b': 1, 'height': 1, 'length': 1, 'n_changed_strings': 1}

    filepath = Path(midi_path)
    f = pretty_midi.PrettyMIDI(filepath.as_posix())
    
    strings = [degree + str(octave) for degree, octave in zip(parameters["degrees"], parameters["octaves"])]
    tuning = Tuning(strings)
    
    tab = Tab(filepath.stem, tuning, f, weights=weights, output_dir = output_dir)
    tab.to_ascii()
    tab.to_json()
