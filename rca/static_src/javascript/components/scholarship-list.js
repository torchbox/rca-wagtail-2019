class ScholarshipList {
    static selector() {
        return '[data-scholarships-url]';
    }

    constructor() {
        this.form = document.getElementById('scholarship-form');
        this.dataURL = this.form.getAttribute('data-scholarships-url');
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

    // Update URL Param
    updateURLParam() {
        const activeOption = this.programmeChooser.options[
            this.programmeChooser.selectedIndex
        ].value;
        const urlParams = new URLSearchParams(window.location.search);
        urlParams.set('programme', activeOption);
        window.location.search = urlParams;
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
            this.updateURLParam();
            this.getData(e);
        });
    }
}

export default ScholarshipList;
