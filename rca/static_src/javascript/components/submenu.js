class SubMenu {
    static selector() {
        return '[data-menu-parent]';
    }

    constructor(node) {
        this.node = node;
        this.levelOne = document.querySelector('[data-nav-level-one]');
        this.activeClass = 'is-visible';
        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('mouseover', () => {
            // get matching child menu
            this.getSubMenu();
        });

        this.node.addEventListener('mouseout', () => {
            this.getSubMenu();
        });
    }

    getSubMenu() {
        const activeMenu = document.querySelector(`[data-nav-level-one] [data-menu-${this.node.dataset.menu}]`);

        // toggle matching child menu
        this.toggleMenu(activeMenu);
    }

    toggleMenu(menu) {
        menu.classList.contains(this.activeClass) ? menu.classList.remove(this.activeClass) : menu.classList.add(this.activeClass);
        this.levelOne.classList.contains(this.activeClass) ? this.levelOne.classList.remove(this.activeClass) : this.levelOne.classList.add(this.activeClass);

    }
}

export default SubMenu;
