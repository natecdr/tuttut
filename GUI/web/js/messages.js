eel.expose(putMessageInOutput);
/**
 * Ecrit un message dans la console.
 * @param {String} message 
 */
function putMessageInOutput(message) {
    const outputNode = document.getElementById("execution-text");
    outputNode.innerHTML = message; // Add the message
}

eel.expose(signalCleaningComplete);
/**
 * Fixe l'état de nettoyage comme terminé.
 */
function signalCleaningComplete() {
    setProcessingState(STATE_COMPLETE);
}