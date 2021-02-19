class GridSizeVariables {
    static selector() {
        return '[data-left-edge]';
    }

    constructor(node) {
        this.node = node;
        this.windowWidth = window.innerWidth;

        this.generateCSSprops();
        this.bindEvents();
    }

    bindEvents() {
        window.addEventListener('resize', () => {
            // Check window width has actually changed and it's not just iOS triggering a resize event on scroll
            // eslint-disable-next-line eqeqeq
            if (window.innerWidth != this.windowWidth) {
                // Update the window width for next time
                this.windowWidth = window.innerWidth;
                this.generateCSSprops();
            }
        });
    }

    generateCSSprops() {
        // Get outer grid size
        const leftEdge = document.querySelector('[data-left-edge]');
        this.leftEdgeCoords = leftEdge.getBoundingClientRect();
        document.documentElement.style.setProperty(
            '--outer-grid-width',
            `${this.leftEdgeCoords.width}px`,
        );

        document.documentElement.style.setProperty(
            '--margin-width',
            `${this.leftEdgeCoords.left}px`,
        );

        // get center grid size
        const gridSelector = document.querySelector('[data-grid-center]');
        this.gridWidth = gridSelector.getBoundingClientRect();
        document.documentElement.style.setProperty(
            '--grid-width',
            `${this.gridWidth.width}px`,
        );
    }
}

export default GridSizeVariables;
