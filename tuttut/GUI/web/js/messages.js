eel.expose(putMessageInOutput);
/**
 * Ecrit un message dans la console.
 * @param {String} message 
 */
function putMessageInOutput(message) {
    const outputNode = document.querySelector('#output textarea');
    outputNode.value += message; // Add the message
    if (!message.endsWith('\n')) {
        outputNode.value += '\n'; // If there was no new line, add one
    }

    outputNode.scrollTop = outputNode.scrollHeight
}

eel.expose(signalCleaningComplete);
/**
 * Fixe l'état de nettoyage comme terminé.
 */
function signalCleaningComplete() {
    setCleaningState(CLEANING_STATE_COMPLETE);
}

eel.expose(colorListElement);
/**
 * Affiche un indicateur de couleur sur un élément de la liste.
 * @param {String} elementId Id de l'élément de la liste
 * @param {String} color Couleur (CSS) de l'indicateur
 */
function colorListElement(elementId, color) {
    const listElement = document.getElementById(elementId);
    listElement.style.borderLeft = "3px solid " + color;
}

eel.expose(isHalted);
/**
 * Vérifie si le nettoyage est interrompu.
 * @returns True si interrompu, False sinon
 */
function isHalted() {
    return halted;
}