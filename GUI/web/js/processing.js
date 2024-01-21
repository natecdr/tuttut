let cleaningState = STATE_NOT_READY;

/**
 * Met à jour l'interface selon l'état courant du nettoyage.
 * @param {String} newState Nouvel état du nettoyage
 */
const setProcessingState = (newState) => {
    cleaningState = newState;

    const outputTextNode = document.getElementById('execution-text');
    const cleanButtonNode = document.getElementById('execute-button');

    switch (newState) {
        case STATE_NOT_READY:
            cleanButtonNode.disabled = true;
            cleanButtonNode.style.backgroundColor = "grey";
            cleanButtonNode.innerHTML = "Please select files";
            return;
        case STATE_READY:
            // Clear output
            cleanButtonNode.disabled = false;
            outputTextNode.value = 'Ready.';
            cleanButtonNode.style.backgroundColor = "blue";
            // Set the main button back to initial value
            cleanButtonNode.innerHTML = "Tabify";
            return;
        case STATE_WORKING:
            // Disable convert button
            cleanButtonNode.disabled = true;
            cleanButtonNode.style.backgroundColor = "red";
            cleanButtonNode.innerHTML = "Working...";
            return;
        case STATE_COMPLETE:
            // Re-enable convert button and re-purpose it
            cleanButtonNode.disabled = false;
            cleanButtonNode.style.backgroundColor = "green";
            cleanButtonNode.innerHTML = "Clear output";
            return;
    }
};

const checkConfigurationComplete = () => {
    if ((selectedMIDIFile !== null) && (selectedOutputDir !== null)) {
        setProcessingState(STATE_READY);
    }
}
 
/**
 * Lance le nettoyage avec les bons paramètres.
 * @param {String} output_folder Chemin du dossier de sortie
 */
const tabify = async () => {
    setProcessingState(STATE_WORKING);

    const parameters = {
        nStrings : document.getElementById("nstrings-opt").value,
        degrees : tuningDegrees,
        octaves : tuningOctaves,
        nFrets : document.getElementById("nfrets-opt").value
    }

    await eel.tabify(selectedMIDIFile, selectedOutputDir, parameters)();
};