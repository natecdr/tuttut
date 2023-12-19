/*
Handle user events
*/

/**
 * Adds a MIDI File
 * @param {Event} event 
 */
const selectMIDIFile = async (event) => {
    const filePath = await askForFile();

    if (filePath !== null) {
        const midiNameNode = document.getElementById('midi-file-path');
        midiNameNode.innerHTML = filePath
        selectedMIDIFile = filePath
    }
};

/**
 * Demande à l'utilisateur un dossier de sortie.
 * @param {Event} event 
 */
const selectOutputDirectory = async (event) => {
    var dirPath = await askForFolder();

    if (dirPath !== null) {
        const outputDirNode = document.getElementById('output-folder-path');
        outputDirNode.innerHTML = dirPath
        selectedOutputDir = dirPath
    }
}

/**
 * Fait des vérifications avant de lancer le nettoyage.
 * @param {Event} event 
 */
const checkAndTabify = async (event) => {
    if (cleaningState === STATE_COMPLETE) { // This is now the clear output button
        setCleaningState(STATE_READY);
        putMessageInOutput("");
        return;
    }

    // If checks have passed, clean selected files
    tabify()
};

/**
 * Initialise les evènements liés à des actions.
 */
const setupEvents = () => {
    // Additional files
    document.getElementById('select-midi-button').addEventListener('click', selectMIDIFile);
    document.getElementById('select-output-folder-button').addEventListener('click', selectOutputDirectory);
    document.getElementById('execute-button').addEventListener('click', checkAndTabify);
};
