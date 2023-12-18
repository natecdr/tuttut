let cleaningState = STATE_READY;

/**
 * Met à jour l'interface selon l'état courant du nettoyage.
 * @param {String} newState Nouvel état du nettoyage
 */
const setCleaningState = (newState) => {
    cleaningState = newState;

    const outputTextNode = document.getElementById('execution-text');
    const cleanButtonNode = document.getElementById('execute-button');

    switch (newState) {
        case STATE_READY:
            // Clear output
            outputTextNode.value = 'dd';
            // Set the main button back to initial value
            cleanButtonNode.innerHTML = "Tabify";
            return;
        case STATE_WORKING:
            // Disable convert button
            cleanButtonNode.style.backgroundColor = "red";
            cleanButtonNode.innerHTML = "Interrupt";
            enableCheckboxes(false);
            return;
        case STATE_COMPLETE:
            // Re-enable convert button and re-purpose it
            cleanButtonNode.disabled = false;
            cleanButtonNode.style.backgroundColor = "#458BC6";
            cleanButtonNode.innerHTML = "Clear output";
            enableCheckboxes(true);
            return;
        case STATE_HALTING:
            cleanButtonNode.disabled = true;
            cleanButtonNode.innerHTML = "Interrupting...";
    }
};

/**
 * Lance le nettoyage avec les bons paramètres.
 * @param {String} output_folder Chemin du dossier de sortie
 */
const tabify = async () => {
    setCleaningState(STATE_WORKING);
    // var preset = getPreset()
    await eel.tabify(selectedMIDIFile, selectedOutputDir)();
};