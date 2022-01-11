class ScholarshipList {
    static selector() {
        return '[data-scholarships-url]';
    }

    constructor() {
        this.form = document.getElementById('scholarship-form');
        this.dataURL = this.form.getAttribute('data-scholarships-url');
        this.baseDataURL = this.dataURL;
        this.programmeChooser = document.getElementById('id_programme');

        this.checkURLParam();
        this.getData();
        this.bindEvents();
    }

    // Get URL Param ID for the programme
    checkURLParam() {
        const urlParams = new URLSearchParams(window.location.search);
        const programme = urlParams.get('programme');
        this.selectProgrammeOption(programme);
    }

    // Get the active Scholarship select option
    getActiveOption() {
        const activeOption = this.programmeChooser.options[
            this.programmeChooser.selectedIndex
        ].value;

        this.updateJSONdata(activeOption);
    }

    // Update JSON data attribute
    updateJSONdata(activeOption) {
        // update json path to follow /scholarship-enquiry/ajax/load-scholarships/?programme=46 pattern
        this.dataURL = `${this.baseDataURL}?programme=${activeOption}`;
        this.getData();
    }

    // Update Programme select option to parsed ID
    selectProgrammeOption(programme) {
        this.programmeChooser.value = programme;
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
                dataLocation.innerHTML = scholarshipsData;
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

            console.log(this.dataURL);
        });
    }
}

export default ScholarshipList;
