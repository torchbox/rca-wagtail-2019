class ProgrammeToggleSwitch {
    static selector() {
        return '[data-study-mode-toggle]';
    }

    constructor(button) {
        this.toggleSwitch = button;
        this.checkbox = this.toggleSwitch.firstElementChild;

        const location_root = window.location.href;

        this.programmes_path = window.location.pathname;

        const paramString = location_root.split('?')[1];
        this.queryString = new URLSearchParams(paramString);
        this.isPartTime = this.queryString.get('part-time');

        this.buttonStatus();
        this.bindEvents();
    }

    buttonStatus() {
        if (this.isPartTime === 'true') {
            this.checkbox.checked = true;
        }

        if (this.isPartTime === false || !this.isPartTime) {
            this.checkbox.checked = false;
        }
    }

    applyToggle() {
        if (!this.isPartTime) {
            this.queryString.set('part-time', 'true');
            const url = `${
                this.programmes_path
            }?${this.queryString.toString()}`;
            window.location = url;
        }

        if (this.isPartTime === 'true') {
            this.queryString.set('part-time', 'false');
            const url = `${
                this.programmes_path
            }?${this.queryString.toString()}`;
            window.location = url;
        }

        if (this.isPartTime === 'false') {
            this.queryString.set('part-time', 'true');
            const url = `${
                this.programmes_path
            }?${this.queryString.toString()}`;
            window.location = url;
        }
    }

    bindEvents() {
        this.toggleSwitch.addEventListener('click', () => this.applyToggle());
    }
}

export default ProgrammeToggleSwitch;
