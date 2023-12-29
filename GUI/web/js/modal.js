/*
* Renders the native JS modal over the window.
* Returns selected option from **buttonOptions** list.
*
* Input:
*   - title: string
*   - description: string
*   - [optional] buttonOptions: string[] = ['Yes', 'No']
*   - [optional]: closeEvent: string = 'Close'
*
* Returns:
*   - Promise<string>
 */
const displayModal = (title, description, buttonOptions=['Yes', 'No'], closeEvent='Close') => {
    const buildTuningInputs = (nStrings) => {
        var degrees = ["C", "D", "E", "F", "G", "A", "B"];

        degreeContainer = document.getElementById("tuning-degree");
        octaveContainer = document.getElementById("tuning-octave");

        degreeContainer.innerHTML = "";
        octaveContainer.innerHTML = "";

        for (i = 0; i<nStrings; i++) {
            //Degrees
            const degreeInput = document.createElement("select");
            degreeInput.addEventListener("change", () => updateTuningDegreeInputs());
            degreeInput.id = "tuning-degree-opt";
            degreeInput.classList.add("tuning-degree-opt");
            for (var ideg = 0; ideg<degrees.length; ideg++) {
                var option = document.createElement("option");
                option.value = degrees[ideg];
                option.text = degrees[ideg];
                degreeInput.appendChild(option);
            }
            degreeInput.value = tuningDegrees[i] ? tuningDegrees[i] : "C";
            degreeContainer.appendChild(degreeInput);

            //Octaves
            const octaveInput = document.createElement("input", type="number", min=0, max=9);
            octaveInput.addEventListener("change", () => updateTuningOctaveInputs());
            octaveInput.classList.add("tuning-octave-opt");
            octaveInput.type = "number";
            octaveInput.min = 0;
            octaveInput.max = 9;
            octaveInput.value = tuningOctaves[i] || 5;
            octaveContainer.appendChild(octaveInput);
        }
        updateTuningDegreeInputs()
        updateTuningOctaveInputs()
    }

    const updateTuningDegreeInputs = () => {
        degreeSelects = document.getElementsByClassName("tuning-degree-opt");
        degrees = Object.values(degreeSelects);
        tuningDegrees = degrees.map(el => el.value);
    }

    const updateTuningOctaveInputs = () => {
        octaveSelects = document.getElementsByClassName("tuning-octave-opt");
        octaves = Object.values(octaveSelects);
        tuningOctaves = octaves.map(el => el.value);
    }

    const modalArea = document.getElementById("modal-area");
    modalArea.classList.remove('modal-coverage-hidden');

    const closeButton = document.getElementById("close-btn")
    const nStringsOpt = document.getElementById("nstrings-opt")

    buildTuningInputs(nStringsOpt.value);
    nStringsOpt.addEventListener("change", () => buildTuningInputs(nStringsOpt.value))

    const clearEventListeners = () => {
        closeButton.removeEventListener('click', (_) => {});
    };

    return new Promise((resolve) => {
        closeButton.addEventListener('click', (_) => {
            clearEventListeners();
            modalArea.classList.add('modal-coverage-hidden');
            resolve(closeEvent);
        });
    })
};
