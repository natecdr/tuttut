import sys
import os

# sys.path.append(os.path.join(sys.path[0], "web_gui"))

import os
import shutil
import traceback

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

def clean_scan(path, output_path, preset): 
    """Nettoie de A à Z un scan.

    Args:
        path (str): Chemin du scan
        output_path (str): Chemin de sortie du scan
        preset (Dict): Paramètres de nettoyage
    """
    ui.print_ui(" Loading scan...")
    pcd, e57 = loadPcdFromE57(path, return_e57=True)
    ui.print_ui(" Detecting outdoor...")
    if is_outdoor(pcd):
        min_percentage = 5
        ui.print_ui("  OUTDOOR")
    else:
        min_percentage = preset["percentage"]
        ui.print_ui("  INDOOR")
    ui.print_ui(" DBSCANing...")
    indices = clean_wide_dbscan(pcd, 
                                voxel_size = preset["voxel_size"],
                                max_dist = preset["max_dist"], 
                                method="percentSignificant", 
                                return_pcd = False, 
                                min_percentage = min_percentage,
                                S=preset["S"]
                                )
    ui.print_ui(" Formatting...")
    res_raw = format_e57_raw(indices, e57)
    ui.print_ui(" Exporting...")
    export_e57(os.path.join(output_path, __get_filename(path)), res_raw, e57)
    ui.print_ui(" Done.")

def clean_files(paths, output_folder, preset):
    """Nettoie des fichiers E57.

    Args:
        paths (str[]): Chemins des fichiers à nettoyer
        output_folder (str): Chemin de sortie
        preset (Dict): Paramètres de nettoyage
    """
    for path in paths:
        if path.endswith(".e57"):
            output_path = output_folder if output_folder != "" else __get_res_path(path)
            ui.print_ui("Current : " + path)
            try:
                if ui.is_halted():
                    ui.print_ui("L'exécution a été interrompue...")
                    ui.color_list_element(path, "red") #Red
                else:
                    ui.color_list_element(path, "orange") #Yellow
                    clean_scan(path, output_path, preset)
                    ui.color_list_element(path, "green") #Green
            except:
                ui.print_ui("^^^^^^^^^^^^^^^^^^^^")
                ui.print_ui(traceback.format_exc())
                ui.print_ui("--------------------")
                shutil.copyfile(path, os.path.join(output_path, __get_filename(path)))
                ui.color_list_element(path, "red") #Red

def path_contains_e57(src_path):
    """Vérifie si un dossier contient des E57.

    Args:
        src_path (str): Chemin du dossier

    Returns:
        bool: True si il contient des E57, False sinon
    """
    for filename in os.listdir(src_path):
        if filename.endswith(".e57"):
            return True
    return False