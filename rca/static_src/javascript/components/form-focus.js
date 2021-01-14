class FormFocus {
    static selector() {
        return '[data-focus]';
    }

    constructor(node) {
        this.formItem = node;
        this.formItemClass = '.form-item';
        this.nearestFormItem = this.formItem.closest(this.formItemClass);
        this.focusClass = 'form-item--has-focus';
        this.hasContentClass = 'form-item--has-content';
        this.bindEvents();
    }

    // Apply focus class
    applyClass() {
        this.nearestFormItem.classList.add(this.focusClass);
    }

    // Remove focus class
    removeClass() {
        // Check if input has content and add content class if it does
        if (this.formItem.value) {
            this.nearestFormItem.classList.add(this.hasContentClass);
            this.nearestFormItem.classList.remove(this.focusClass);
        } else {
            this.nearestFormItem.classList.remove(this.focusClass);
            this.nearestFormItem.classList.remove(this.hasContentClass);
        }
    }

    bindEvents() {
        this.formItem.addEventListener('focusin', () => this.applyClass());
        this.formItem.addEventListener('focusout', () => this.removeClass());
    }
}

export default FormFocus;
