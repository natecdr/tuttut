/*
Util functions
*/

const flatMap = (xs) => xs.reduce((x,y ) => x.concat(y), []); // Not all browsers have Array.flatMap

/*
* Equivalent of Python zip(*args) function. Usage:
*
* for (let [var1, ..., varN] of zip(arr1, ..., arrN)) {
*   ...
* }
*/
const zip = (...arrays) => [...arrays[0]].map((_,index) => arrays.map(arr => arr[index]))

const doesFileExist = async (path) => {
    return await eel.does_file_exist(path)();
};

const doesFolderExist = async (path) => {
    return await eel.does_folder_exist(path)();
};

/**
 * Demande à l'utilisateur un/des fichiers.
 * @returns Liste de chemins de fichiers
 */
const askForFile = async () => {
    return await eel.ask_file()();
};

/**
 * Demande à l'utilisateur un dossier.
 * @returns Chemin d'un dossier
 */
const askForFolder = async () => {
    return await eel.ask_folder()();
};

/**
 * Retourne les fichiers contenus  dans un dossier.
 * @param {String} path Chemin du dossier.
 * @returns Liste de chemins de fichiers
 */
const getFilesInFolder = async (path) => {
    return await eel.get_files_in_folder(path)();
};