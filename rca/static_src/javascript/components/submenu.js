class SubMenu {
    static selector() {
        return '[data-menu-parent]';
    }

    constructor(node) {
        this.node = node;
        this.levelTwo = document.querySelector('[data-nav-level-two]');
        this.levelThree = document.querySelector('[data-nav-level-three]');
        this.activeClass = 'is-visible';
        this.bindEventListeners();
    }

    bindEventListeners() {
        // todo - change depending on window size
        const condition = false;

        if(condition) {
            this.node.addEventListener('mouseover', (e) => {
                // get matching child menu
                if (e.target.tagName === 'A') {
                    this.getMenuContext(e.target.dataset);
                }
            });

            this.node.addEventListener('mouseout', (e) => {
                if (e.target.tagName === 'A') {
                    this.getMenuContext(e.target.dataset);
                }
            });

            this.levelThree.addEventListener('mouseover', (e) => {
                this.levelTwo.classList.add(this.activeClass);
                if (e.target.tagName === 'A') {
                    this.showPrevSubMenu(e.target.dataset.menu);
                }
            });

            this.levelThree.addEventListener('mouseout', (e) => {
                this.levelTwo.classList.remove(this.activeClass);
                if (e.target.tagName === 'A') {
                    this.hidePrevSubMenu(e.target.dataset.menu);
                }
            });
        } else {
            this.node.addEventListener('click', (e) => {
                e.preventDefault();
                this.getMenuContext(e.target.dataset);
            });
        }
    }

    getMenuContext(dataset) {
        const menuLevel = dataset.targetLevel;
        const menu = dataset.menu;

        // slide out the menu drawer
        this.toggleDrawer(menuLevel);

        // show the sub-menu
        this.toggleSubMenu(menuLevel, menu);
    }

    // keep level two open if we're on level three
    showPrevSubMenu(menu) {
        const targetMenu = document.querySelector(`[data-nav-level-two] [data-menu-${menu}]`);
        targetMenu.classList.add(this.activeClass);
    }

    // hide level two if we leave level three
    hidePrevSubMenu(menu) {
        const targetMenu = document.querySelector(`[data-nav-level-two] [data-menu-${menu}]`);
        targetMenu.classList.remove(this.activeClass);
    }

    toggleSubMenu(menuLevel, menu) {
        const targetMenu = document.querySelector(`[data-nav-level-${menuLevel}] [data-menu-${menu}]`);
        targetMenu.classList.contains(this.activeClass) ? targetMenu.classList.remove(this.activeClass) : targetMenu.classList.add(this.activeClass);
    }

    toggleDrawer(menuLevel) {
        const drawer = document.querySelector(`[data-nav-level-${menuLevel}]`);
        drawer.classList.contains(this.activeClass) ? drawer.classList.remove(this.activeClass) : drawer.classList.add(this.activeClass);
    }
}

export default SubMenu;
