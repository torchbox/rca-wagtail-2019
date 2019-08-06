class Menu {
    static selector() {
        return '[data-menu-toggle]';
    }

    constructor(node) {
        this.node = node;
        this.body = document.querySelector('body');
        this.activeClass = 'nav-open';

        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('click', (e) => {
            e.preventDefault();
            this.toggle();
        });
    }

    toggle() {
        this.body.classList.contains(this.activeClass) ? this.close() : this.open();
    }

    open() {
        this.body.classList.add(this.activeClass);
    }

    close() {
        this.body.classList.remove(this.activeClass);
    }
}

export default Menu;
