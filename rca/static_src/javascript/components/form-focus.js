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

    // Apply focus class
    applyClass() {
        this.formItem.classList.add(this.hasFocusClass);
    }

    // Remove focus class
    removeClass() {
        // Check if input has content and add content class if it does
        if (this.formType === 'textarea') {
            if (this.formFieldTextarea.value) {
                this.formItem.classList.add(this.hasContentClass);
                this.formItem.classList.remove(this.hasFocusClass);
            } else {
                this.formItem.classList.remove(this.hasFocusClass);
                this.formItem.classList.remove(this.hasContentClass);
            }
        }

        if (this.formType === 'input') {
            if (this.formFieldInput.value) {
                this.formItem.classList.add(this.hasContentClass);
                this.formItem.classList.remove(this.hasFocusClass);
            } else {
                this.formItem.classList.remove(this.hasFocusClass);
                this.formItem.classList.remove(this.hasContentClass);
            }
        }
    }

    bindEvents() {
        if (this.formType === 'textarea') {
            this.formFieldTextarea.addEventListener('focusin', () =>
                this.applyClass(),
            );
            this.formFieldTextarea.addEventListener('focusout', () =>
                this.removeClass(),
            );
            this.formFieldTextarea.addEventListener('input', () =>
                this.applyClass(),
            );
        }

        if (this.formType === 'input') {
            this.formFieldInput.addEventListener('focusin', () =>
                this.applyClass(),
            );
            this.formFieldInput.addEventListener('focusout', () =>
                this.removeClass(),
            );
            this.formFieldInput.addEventListener('input', () =>
                this.applyClass(),
            );
        }
    }
}

export default FormFocus;
