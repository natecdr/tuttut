/*
Handle user events
*/

/**
 * Ajoute à la liste des fichiers.
 * @param {Array} files Fichiers à ajouter
 */
const addAdditionalFiles = async (files) => {
    if (files !== null) {
        const filesListNode = document.getElementById('files-list');
        files.forEach(file => {
            addFile(filesListNode, file);
        });
    }
};

/**
 * Ajoute des fichiers après les avoir seléctionné indépendamment.
 * @param {Event} event 
 */
const additionalFilesAddFiles = async (event) => {
    const files = await askForFiles();
    addAdditionalFiles(files)
};

/**
 * Ajoute des fichiers après avoir seléctionné un dossier.
 * @param {Event} event 
 */
const additionalFilesAddFolder = async (event) => {
    const folder = await askForFolder();
    const files = await getFilesInFolder(folder);
    addAdditionalFiles(files)
};

/**
 * Fait des vérifications avant de lancer le nettoyage.
 * @param {Event} event 
 */
const checkCleanSelectedFiles = async (event) => {
    if (cleaningState === CLEANING_STATE_CLEANING) {
        if (!halted) {
            halted = true;
        }
        setCleaningState(CLEANING_STATE_HALTING);
        return;
    }
    if (cleaningState === CLEANING_STATE_COMPLETE) { // This is now the clear output button
        halted = false;
        setCleaningState(CLEANING_STATE_READY);
        return;
    }

    // If checks have passed, clean selected files
    cleanSelectedFiles()
};

/**
 * Demande à l'utilisateur un dossier de sortie.
 * @param {Event} event 
 */
const selectOutputDirectory = async (event) => {
    var resPath = await askForFolder();
    document.getElementById("output-directory-textarea").value = resPath;
}

/**
 * Initialise les evènements liés à des actions.
 */
const setupEvents = () => {
    // Additional files
    document.getElementById('select-midi').addEventListener('click', additionalFilesAddFiles);
};
