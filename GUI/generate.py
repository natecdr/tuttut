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

def __get_filename(path):
    """Retourne le nom de fichier à partir d'un chemin.

    Args:
        path (str): Chemin du fichier

    Returns:
        str: Nom du fichier
    """
    return path.split(os.sep)[-1]

def __get_res_path(path):
    """Retourne le chemin de sortie d'un fichier (dossier_du_scan/clean)

    Args:
        path (str): Chemin du fichier

    Returns:
        str: Chemin du dossier de sortie
    """
    dir_path = os.sep.join(path.split(os.sep)[:-1])
    res_path = os.path.join(dir_path, "clean")
    if not os.path.isdir(res_path):
        os.mkdir(res_path)
    return res_path

def tabify(midi_path, output_dir): 
    """Nettoie de A à Z un scan.

    Args:
        path (str): Chemin du scan
        output_path (str): Chemin de sortie du scan
        preset (Dict): Paramètres de nettoyage
    """
    gui.print_ui(" Loading scan...")
    # pcd, e57 = loadPcdFromE57(path, return_e57=True)
    # gui.print_ui(" Detecting outdoor...")
    # if is_outdoor(pcd):
    #     min_percentage = 5
    #     gui.print_ui("  OUTDOOR")
    # else:
    #     min_percentage = preset["percentage"]
    #     gui.print_ui("  INDOOR")
    # gui.print_ui(" DBSCANing...")
    # indices = clean_wide_dbscan(pcd, 
    #                             voxel_size = preset["voxel_size"],
    #                             max_dist = preset["max_dist"], 
    #                             method="percentSignificant", 
    #                             return_pcd = False, 
    #                             min_percentage = min_percentage,
    #                             S=preset["S"]
    #                             )
    # gui.print_ui(" Formatting...")
    # res_raw = format_e57_raw(indices, e57)
    # gui.print_ui(" Exporting...")
    # export_e57(os.path.join(output_path, __get_filename(path)), res_raw, e57)
    # gui.print_ui(" Done.")
    
    weights = {'b': 1, 'height': 1, 'length': 1, 'n_changed_strings': 1}

    filepath = Path(midi_path)
    f = pretty_midi.PrettyMIDI(filepath.as_posix())
    tab = Tab(filepath.stem, Tuning(), f, weights=weights, output_dir = output_dir)
    # tab = Tab(file.stem, Tuning([Note(69), Note(64), Note(60), Note(67)]), f, weights=weights)
    tab.to_ascii()
    tab.to_json()
