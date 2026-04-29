class ScholarshipFeeStatusToggle {
    static selector() {
        return '[data-scholarship-toggle]';
    }

    constructor(button) {
        this.toggleSwitch = button;
        this.checkbox = this.toggleSwitch.firstElementChild;
        this.labelHome = this.toggleSwitch.querySelector(
            '.toggle-switch__label--first',
        );
        this.labelOverseas = this.toggleSwitch.querySelector(
            '.toggle-switch__label--last',
        );
        this.resetButton = document.querySelector('[data-filters-reset]');

        let locationRoot = window.location.href;
        locationRoot = locationRoot.replace('#results', '');

        this.path = window.location.pathname;

        const paramString = locationRoot.split('?')[1];
        this.queryString = new URLSearchParams(paramString);
        this.feeStatus = this.queryString.get('fee-status');

        this.setCheckboxState();
        this.bindEvents();
    }

    setCheckboxState() {
        const isOverseas = this.feeStatus === 'international';
        this.checkbox.checked = isOverseas;
        this.updateLabels(isOverseas);
        if (this.feeStatus && this.resetButton) {
            this.resetButton.classList.remove('reset--hidden');
        }
    }

    updateLabels(isOverseas) {
        // Make sure that the selected label is highlighted.
        this.labelHome.classList.toggle(
            'toggle-switch__label--selected',
            !isOverseas,
        );
        this.labelOverseas.classList.toggle(
            'toggle-switch__label--selected',
            isOverseas,
        );
    }

    applyToggle() {
        const feeStatus = this.checkbox.checked ? 'international' : 'uk';
        this.queryString.set('fee-status', feeStatus);
        window.location = `${this.path}?${this.queryString.toString()}#results`;
    }

    bindEvents() {
        this.toggleSwitch.addEventListener('click', () => this.applyToggle());
    }
}

export default ScholarshipFeeStatusToggle;
