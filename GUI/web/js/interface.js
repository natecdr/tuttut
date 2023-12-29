/*
Handle visual events
*/

/**
 * Change le préréglage du nettoyage.
 */
const changePreset = () => {
    var preset_name = document.getElementById("preset-opt").value
    fetch("presets.json")
     .then(response => response.json())
     .then(json => updateParameters(json[preset_name]));
}

/**
 * Met à jour les paramètres dans l'onglet "Avancé" selon le préréglage.
 * @param {String} preset Préréglage seléctionné
 */
const updateParameters = (preset) => {
    document.getElementById("cluster-percentage-opt").value = preset["percentage"]
    document.getElementById("max-dist-opt").value = preset["max_dist"]
    document.getElementById("voxel-size-opt").value = preset["voxel_size"]
    document.getElementById("sensivity-opt").value = preset["S"]
}

/**
 * Retourne un objet contenant les paramètres du preset
 * @returns 
 */
const getPreset = () => {
    return {
        "percentage": parseInt(document.getElementById("cluster-percentage-opt").value),
        "max_dist": parseFloat(document.getElementById("max-dist-opt").value),
        "voxel_size": parseFloat(document.getElementById("voxel-size-opt").value),
        "S": parseInt(document.getElementById("sensivity-opt").value)
    }
}
