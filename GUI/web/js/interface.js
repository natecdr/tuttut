/*
Handle visual events
*/

/**
 * Gère la liste des scans seléctionnés quand une boîte est cochée/décochée.
 * @param {CheckBox} checkBox Boîte à cocher concernée
 */
function handleCheck(checkBox) {
    if (checkBox.checked) {
        if (!selectedScans.includes(checkBox.value)) {
            selectedScans.push(checkBox.value);
        }
    } else {
        const index = selectedScans.indexOf(checkBox.value);
        if (index > -1) {
            selectedScans.splice(index, 1);
        }
    }            
}

/**
 * Ajoute un scan à la liste.
 * @param {*} parentNode Objet liste
 * @param {*} source Chemin du scan
 */
const addFile = (parentNode, source) => {
    const sourceElements = source.split(/[/\\]/);
    const filename = sourceElements.pop()
    // const dirPath = sourceElements.join("/")
    if (!source.endsWith(".e57") || scansList.includes(source)) { return; }

    const wrapper = document.createElement('div');
    parentNode.appendChild(wrapper);
    const checkBox = document.createElement('input')
    wrapper.appendChild(checkBox)
    const sourceText = document.createElement('label');
    wrapper.appendChild(sourceText);

    wrapper.classList.add('input-file');
    wrapper.id = source
    
    checkBox.type="checkbox"
    checkBox.name = "fileCheckbox"
    checkBox.id = source + "-chk"
    checkBox.value = source

    scansList.push(source)

    checkBox.addEventListener("click", (event) => {
        focused = document.getElementsByClassName("focused-scan")[0]
        if (focused !== undefined) {
            focused.classList.remove("focused-scan");
            if (event.shiftKey) {
                focusedCheckbox = focused.querySelector("input");
                checkboxes = document.getElementsByName("fileCheckbox");
                firstIndex = scansList.indexOf(focusedCheckbox.value);
                lastIndex = scansList.indexOf(checkBox.value);

                for (var i = Math.min(firstIndex, lastIndex); i<=Math.max(firstIndex, lastIndex); i++) {
                    checkboxes[i].checked = checkBox.checked;  
                    handleCheck(checkboxes[i]);
                }
            }
        }
        wrapper.classList.add("focused-scan");

        handleCheck(checkBox);  
    });

    sourceText.htmlFor = source + "-chk"
    sourceText.appendChild(document.createTextNode(filename))
    sourceText.classList.add('input-file-label')
    sourceText.classList.add('noselect');
};

/**
 * Seléctionne/déseléctionne toutes les cases.
 * @param {CheckBox} obj Case "Cocher tout"
 */
const selectAll = (obj) => {
    checkboxes = document.getElementsByName("fileCheckbox");
    for (var i = 0; i<checkboxes.length; i++) {
        checkboxes[i].checked = obj.checked;    
        handleCheck(checkboxes[i]);     
    }
}

/**
 * Affiche les options selon l'onglet seléctionné.
 * @param {Object} obj Objet onglat
 */
const displayOptionsTab = (obj) => {
    var currentlyActiveLi = document.getElementsByClassName("active-opt")[0];
    if (currentlyActiveLi.id !== obj.id) {
        currentlyActiveLi.classList.remove("active-opt")

        var currentlyActiveTab = document.getElementsByClassName("active-opt-tab")[0];
        currentlyActiveTab.classList.remove("active-opt-tab")

        obj.classList.add("active-opt")

        switch (obj.id) {
            case "general-opt":
                document.getElementById("general-options").classList.add("active-opt-tab");
                return;
            case "advanced-opt":
                document.getElementById("advanced-options").classList.add("active-opt-tab");
                return;
        }
    }
}

/**
 * Active ou désactive les cases à cocher.
 * @param {*} enabled Active si True, Désactive sinon
 */
const enableCheckboxes = (enabled) => {
    checkboxes = document.getElementsByName("fileCheckbox");
    for (var i = 0; i<checkboxes.length; i++) {
        checkboxes[i].disabled = !enabled;
    }
}

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
