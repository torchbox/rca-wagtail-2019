class ActualHeight {
    constructor() {
        this.createCustomProperty();
        this.bindEvents();
    }

    createCustomProperty() {
        // Work out the full height then divide by 100 to work out what 1vh should be (excluding any toolbars)
        const vh = window.innerHeight * 0.01;
        // Then we set the value in the --vh custom property to the root of the document
        document.documentElement.style.setProperty('--vh', `${vh}px`);
    }

    bindEvents() {
        window.addEventListener(
            'resize',
            () => {
                this.createCustomProperty();
            },
            { passive: true },
        );
    }
}

export default ActualHeight;
