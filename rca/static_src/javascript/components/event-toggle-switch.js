class EventToggleSwitch {
    static selector() {
        return '[data-toggle-switch]';
    }

    constructor(button) {
        this.toggleSwitch = button;
        this.checkbox = this.toggleSwitch.firstElementChild;

        let location_root = window.location.href;
        location_root = location_root.replace('#results', '');

        this.events_path = window.location.pathname;

        const paramString = location_root.split('?')[1];
        this.queryString = new URLSearchParams(paramString);
        this.tense = this.queryString.get('tense');

        this.buttonStatus();
        this.bindEvents();
    }

    buttonStatus() {
        if (this.tense === 'past') {
            this.checkbox.checked = true;
        }

        if (this.tense === 'future' || !this.tense) {
            this.checkbox.checked = false;
        }
    }

    applyToggle() {
        if (!this.tense) {
            this.queryString.set('tense', 'past');
            const url = `${
                this.events_path
            }?${this.queryString.toString()}#results`;
            window.location = url;
        }

        if (this.tense === 'past') {
            this.queryString.set('tense', 'future');
            const url = `${
                this.events_path
            }?${this.queryString.toString()}#results`;
            window.location = url;
        }

        if (this.tense === 'future') {
            this.queryString.set('tense', 'past');
            const url = `${
                this.events_path
            }?${this.queryString.toString()}#results`;
            window.location = url;
        }
    }

    bindEvents() {
        this.toggleSwitch.addEventListener('click', () => this.applyToggle());
    }
}

export default EventToggleSwitch;
