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

    checkConfigurationComplete();
};

/**
 * Asks the user for an output directory
 * @param {Event} event 
 */
const selectOutputDirectory = async (event) => {
    var dirPath = await askForFolder();

    if (dirPath !== null) {
        const outputDirNode = document.getElementById('output-folder-path');
        outputDirNode.innerHTML = dirPath
        selectedOutputDir = dirPath
    }

    checkConfigurationComplete();
}

/**
 * Checks stuff befor tabifying
 * @param {Event} event 
 */
const checkAndTabify = async (event) => {
    if (cleaningState === STATE_COMPLETE) { // This is now the clear output button
        setProcessingState(STATE_READY);
        putMessageInOutput("");
        return;
    }

    // If checks have passed, clean selected files
    tabify()
};

/**
 * Initializes events linked to user actions
 */
const setupEvents = () => {
    // Additional files
    setProcessingState(STATE_NOT_READY);

    document.getElementById('select-midi-button').addEventListener('click', selectMIDIFile);
    document.getElementById('select-output-folder-button').addEventListener('click', selectOutputDirectory);
    document.getElementById('execute-button').addEventListener('click', checkAndTabify);
    document.getElementById('settings-button').addEventListener('click', displayModal);
};
