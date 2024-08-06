class TableHint {
    static selector() {
        return '[data-table-hint]';
    }

    constructor(node) {
        this.node = node;
        this.button = node.querySelector('[data-table-hint-button]');
        this.bindEvents();

        this.prefersReducedMotion =
            window.matchMedia(`(prefers-reduced-motion: reduce)`).matches ===
            true;
    }

    bindEvents() {
        // Once the user scrolls, remove the button and hint and don't reshow them
        this.node.addEventListener('scroll', () => {
            if (this.node.scrollLeft > 0) {
                this.node.classList.add('is-scrolling');
            }
        });

        this.button.addEventListener('click', () => {
            this.node.scroll({
                top: 0,
                left: 500,
                behavior: this.prefersReducedMotion ? 'auto' : 'smooth',
            });
        });
    }
}

export default TableHint;
