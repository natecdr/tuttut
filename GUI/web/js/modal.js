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
            const degreeInput = document.createElement("select");
            degreeInput.addEventListener("change", () => getTuningDegreeInputs());
            degreeInput.id = "tuning-degree-opt";
            degreeInput.classList.add("tuning-degree-opt");
            for (var ideg = 0; ideg<degrees.length; ideg++) {
                var option = document.createElement("option");
                option.value = degrees[ideg];
                option.text = degrees[ideg];
                degreeInput.appendChild(option);
            }
            degreeContainer.appendChild(degreeInput);

            const octaveInput = document.createElement("input", type="number", min=0, max=9);
            octaveInput.addEventListener("change", () => getTuningOctaveInputs());
            octaveInput.classList.add("tuning-octave-opt");
            octaveInput.type = "number";
            octaveInput.min = 0;
            octaveInput.max = 9;
            octaveInput.value = 5;
            octaveContainer.appendChild(octaveInput);
        }
    }

    const getTuningDegreeInputs = () => {
        degreeSelects = document.getElementsByClassName("tuning-degree-opt");
        degrees = Object.values(degreeSelects);
        return degrees.map(el => el.value);
    }

    const getTuningOctaveInputs = () => {
        octaveSelects = document.getElementsByClassName("tuning-octave-opt");
        octaves = Object.values(octaveSelects);
        return octaves.map(el => el.value);
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
