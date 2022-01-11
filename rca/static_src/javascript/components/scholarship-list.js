class ScholarshipList {
    static selector() {
        return '[data-scholarships-url]';
    }

    constructor() {
        this.form = document.getElementById('scholarship-form');
        this.dataURL = this.form.getAttribute('data-scholarships-url');
        this.programmeChooser = document.getElementById('id_programme');

        this.getData();
        this.bindEvents();
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
                        return `<li><label for="id_scholarships_${index}"><input id="id_scholarships_${index}" type="checkbox" name="scholarships" value="${item.id}">${item.title}</label></li>`;
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
            this.getData(e);
        });
    }
}

export default ScholarshipList;
