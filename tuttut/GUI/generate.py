import sys
import os
import pretty_midi
from pathlib import Path

sys.path.append("./..")

from tuttut.logic.tab import Tab
from tuttut.logic.theory import Tuning

def tabify(midi_path, output_dir, parameters): 
    """Convertissez un fichier MIDI en tablature ASCII et écrivez-le dans output_dir.

    Args:
        midi_path (str): Chemin du fichier MIDI
        output_dir (str): Dossier où écrire la tablature (.txt)
        parameters (Dict): Paramètres de la tablature ("degrees", "octaves", "nFrets")

    Returns:
        Tab: La tablature générée à partir du fichier MIDI
    """
    
    weights = {'b': 1, 'height': 1, 'length': 1, 'n_changed_strings': 1}

    filepath = Path(midi_path)
    f = pretty_midi.PrettyMIDI(filepath.as_posix())
    
    strings = [degree + str(octave) for degree, octave in zip(parameters["degrees"], parameters["octaves"])]
    tuning = Tuning(strings, nfrets=int(parameters["nFrets"]))
    
    tab = Tab(filepath.stem, tuning, f, weights=weights, output_dir = output_dir)
    tab.to_ascii()

    return tab
