let cleaningState = STATE_NOT_READY;

/**
 * Updates the interface according to the new processing state
 * @param {String} newState New processing state
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

/**
 * Checks that the input MIDI and output folder have been set
 */
const checkConfigurationComplete = () => {
    if ((selectedMIDIFile !== null) && (selectedOutputDir !== null)) {
        setProcessingState(STATE_READY);
    }
}
 
/**
 * Launches the processing
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