eel.expose(putMessageInOutput);
/**
 * Writes a messages in the output
 * @param {String} message 
 */
function putMessageInOutput(message) {
    const outputNode = document.getElementById("execution-text");
    outputNode.innerHTML = message; // Add the message
}

eel.expose(signalProcessingComplete);
/**
 * Sets the processing as complete
 */
function signalProcessingComplete() {
    setProcessingState(STATE_COMPLETE);
}