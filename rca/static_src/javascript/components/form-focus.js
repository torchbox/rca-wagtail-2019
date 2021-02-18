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
        if (this.formType === 'textarea') {
            if (
                this.formFieldTextarea.value &&
                this.formFieldTextarea === document.activeElement
            ) {
                this.formItem.classList.add(
                    this.hasContentClass,
                    this.hasFocusClass,
                );
            } else if (this.formFieldTextarea.value) {
                this.formItem.classList.add(this.hasContentClass);
                this.formItem.classList.remove(this.hasFocusClass);
            } else if (this.formFieldTextarea === document.activeElement) {
                this.formItem.classList.add(this.hasFocusClass);
            } else {
                this.formItem.classList.remove(
                    this.hasFocusClass,
                    this.hasContentClass,
                );
            }
        }

        if (this.formType === 'input') {
            if (
                this.formFieldInput.value &&
                this.formFieldInput === document.activeElement
            ) {
                this.formItem.classList.add(
                    this.hasContentClass,
                    this.hasFocusClass,
                );
            } else if (this.formFieldInput.value) {
                this.formItem.classList.add(this.hasContentClass);
                this.formItem.classList.remove(this.hasFocusClass);
            } else if (this.formFieldInput === document.activeElement) {
                this.formItem.classList.add(this.hasFocusClass);
            } else {
                this.formItem.classList.remove(
                    this.hasFocusClass,
                    this.hasContentClass,
                );
            }
        }
    }

    checkFormItemStatus() {}

    bindEvents() {
        if (this.formType === 'textarea') {
            this.formFieldTextarea.addEventListener('input', () =>
                this.applyClass(),
            );
            this.formFieldTextarea.addEventListener('focusin', () =>
                this.applyClass(),
            );
            this.formFieldTextarea.addEventListener('focusout', () =>
                this.applyClass(),
            );
        }

        if (this.formType === 'input') {
            this.formFieldInput.addEventListener('input', () =>
                this.applyClass(),
            );
            this.formFieldInput.addEventListener('focusin', () =>
                this.applyClass(),
            );
            this.formFieldInput.addEventListener('focusout', () =>
                this.applyClass(),
            );
        }
    }
}

export default FormFocus;
