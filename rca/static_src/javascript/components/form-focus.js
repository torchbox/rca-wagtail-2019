class FormFocus {
    static selector() {
        return '[data-focus]';
    }

    constructor(node) {
        this.formItem = node;
        this.formFieldInput = this.formItem.querySelector('input');
        this.formFieldTextarea = this.formItem.querySelector('textarea');
        this.formType = this.formItem.dataset.focustype;
        this.hasFocusClass = 'form-item--has-focus';
        this.hasContentClass = 'form-item--has-content';
        this.bindEvents();
    }

    // Apply state class
    applyStateClass() {
        if (this.formType === 'textarea') {
            this.checkState(this.formFieldTextarea);
        }

        if (this.formType === 'input') {
            this.checkState(this.formFieldInput);
        }
    }

    checkState(el) {
        if (el.value && el === document.activeElement) {
            this.formItem.classList.add(
                this.hasContentClass,
                this.hasFocusClass,
            );
        } else if (el.value) {
            this.formItem.classList.add(this.hasContentClass);
            this.formItem.classList.remove(this.hasFocusClass);
        } else if (el === document.activeElement) {
            this.formItem.classList.add(this.hasFocusClass);
        } else {
            this.formItem.classList.remove(
                this.hasFocusClass,
                this.hasContentClass,
            );
        }
    }

    bindEvents() {
        if (this.formType === 'textarea') {
            // Input is required to detect autocomplete trigger in Chrome
            this.formFieldTextarea.addEventListener('input', () =>
                this.applyStateClass(),
            );
            this.formFieldTextarea.addEventListener('focusin', () =>
                this.applyStateClass(),
            );
            this.formFieldTextarea.addEventListener('focusout', () =>
                this.applyStateClass(),
            );
        }

        if (this.formType === 'input') {
            // Input is required to detect autocomplete trigger in Chrome
            this.formFieldInput.addEventListener('input', () =>
                this.applyStateClass(),
            );
            this.formFieldInput.addEventListener('focusin', () =>
                this.applyStateClass(),
            );
            this.formFieldInput.addEventListener('focusout', () =>
                this.applyStateClass(),
            );
        }
    }
}

export default FormFocus;
