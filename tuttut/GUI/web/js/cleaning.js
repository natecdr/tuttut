let cleaningState = CLEANING_STATE_READY;

/**
 * Met à jour l'interface selon l'état courant du nettoyage.
 * @param {String} newState Nouvel état du nettoyage
 */
const setCleaningState = (newState) => {
    cleaningState = newState;

    const outputSectionNode = document.getElementById('output');
    const outputTextAreaNode = outputSectionNode.querySelector('textarea');
    const cleanButtonNode = document.getElementById('clean-button');

    switch (newState) {
        case CLEANING_STATE_READY:
            // Clear output
            outputTextAreaNode.value = '';
            // Set the main button back to initial value
            cleanButtonNode.innerHTML = "nettoyer";
            return;
        case CLEANING_STATE_CLEANING:
            // Disable convert button
            cleanButtonNode.style.backgroundColor = "red";
            cleanButtonNode.innerHTML = "Interrompre le nettoyage";
            enableCheckboxes(false);
            return;
        case CLEANING_STATE_COMPLETE:
            // Re-enable convert button and re-purpose it
            cleanButtonNode.disabled = false;
            cleanButtonNode.style.backgroundColor = "#458BC6";
            cleanButtonNode.innerHTML = "clear output";
            enableCheckboxes(true);
            return;
        case CLEANING_STATE_HALTING:
            cleanButtonNode.disabled = true;
            cleanButtonNode.innerHTML = "En cours d'interruption...";
    }
};

/**
 * Lance le nettoyage avec les bons paramètres.
 * @param {String} output_folder Chemin du dossier de sortie
 */
const cleanSelectedFiles = async (output_folder) => {
    setCleaningState(CLEANING_STATE_CLEANING);
    var output_folder = document.getElementById("output-directory-textarea").value;
    var preset = getPreset()
    await eel.clean_files(selectedScans, output_folder, preset)();
};