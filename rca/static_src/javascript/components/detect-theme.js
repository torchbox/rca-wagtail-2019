class DetectTheme {
    static selector() {
        return '[data-theme-detect]';
    }

    constructor(node) {
        this.container = node;
        this.detect();
        this.bindEvents();
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
        const a = document.getElementsByClassName('bg--dark');
        [...a].forEach((x) => (x.className += ' bg--light'));
        [...a].forEach((x) => x.classList.remove('bg--dark'));
    }

    setDarkTheme() {
        const a = document.getElementsByClassName('bg--light');
        [...a].forEach((x) => (x.className += ' bg--dark'));
        [...a].forEach((x) => x.classList.remove('bg--light'));
    }
}

export default DetectTheme;
