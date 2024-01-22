/*
Handle the initialisation of the ui
*/

/**
 * Initializes the ui
 */
window.addEventListener("load", async () => {
    await eel.initialise()();

    // Setup ui events (for static content) and setup initial state
    setupEvents();

    // If the server stops, close the UI
    window.eel._websocket.addEventListener('close', e => window.close());
    document.getElementById('spinner-root').style.display = 'none';
});
