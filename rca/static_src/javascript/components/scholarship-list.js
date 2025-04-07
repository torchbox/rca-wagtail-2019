class ScholarshipList {
    static selector() {
        return '[data-scholarships-url]';
    }

    constructor() {
        this.form = document.getElementById('scholarship-form');
        this.dataURL = this.form.getAttribute('data-scholarships-url');
        this.baseDataURL = this.dataURL;
        this.programmeChooser = document.getElementById('id_programme');
        this.bindEvents();
    }

    // Get the active Scholarship select option
    getActiveOption() {
        const activeOption =
            this.programmeChooser.options[this.programmeChooser.selectedIndex]
                .value;

        this.updateJSONdata(activeOption);
    }

    // Update JSON data attribute
    updateJSONdata(activeOption) {
        // update json path to follow /scholarship-enquiry/ajax/load-scholarships/?programme=46 pattern
        if (activeOption !== null) {
            this.dataURL = `${this.baseDataURL}?programme=${activeOption}`;
            this.form.setAttribute('data-scholarships-url', this.dataURL);
            this.getData();
        }
    }

    // Update Programme select option to parsed ID
    selectProgrammeOption(programme) {
        this.programmeChooser.value = programme;

        this.updateJSONdata(programme);
    }

    getData() {
        // Ideally this would be refactored to use fetch
        const xmlhttp = new XMLHttpRequest();
        xmlhttp.onreadystatechange = function getScholarships() {
            if (this.readyState === 4 && this.status === 200) {
                const dataLocation = document.getElementById('id_scholarships');
                const scholarships = JSON.parse(this.responseText);
                const scholarshipsData = scholarships
                    .map((item, index) => {
                        return `
                        <li>
                            <label for="id_scholarships_${index}">
                                <input id="id_scholarships_${index}" type="checkbox" name="scholarships" value="${item.id}">
                                ${item.title}
                            </label>
                        </li>`;
                    })
                    .join('');
                if (scholarships.length === 0) {
                    dataLocation.innerHTML =
                        '<p class="body body--two" style="color: red;">There are no scholarships currently available for this programme.</p>';
                } else {
                    dataLocation.innerHTML = scholarshipsData;
                }
            }
        };
        xmlhttp.open('GET', this.dataURL, true);
        xmlhttp.send();
    }

    bindEvents() {
        // Check when programme select is changed, and replaces scholarships accordingly
        this.programmeChooser.addEventListener('input', (e) => {
            this.getActiveOption();
            this.getData(e);
        });
    }
}

export default ScholarshipList;
