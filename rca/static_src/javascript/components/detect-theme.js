class DetectTheme {
    static selector() {
        return '[data-theme-detect]';
    }

    constructor(node) {
        this.container = node;
        this.detect();
    }

    detect() {
        if (
            window.matchMedia &&
            window.matchMedia('(prefers-color-scheme: dark)').matches
        ) {
            this.setDarkTheme();
        } else {
            this.setLightTheme();
        }
    }

    setLightTheme() {
        const elements = document.querySelectorAll('.bg--dark');

        elements.forEach((item) => {
            item.classList.remove('bg--dark');
            item.classList.add('bg--light');
        });
    }

    setDarkTheme() {
        const elements = document.querySelectorAll('.bg--light');

        elements.forEach((item) => {
            item.classList.remove('bg--light');
            item.classList.add('bg--dark');
        });
    }
}

export default DetectTheme;
