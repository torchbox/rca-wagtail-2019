class SubMenu {
    static selector() {
        return '[data-menu-parent]';
    }

    constructor(node) {
        this.node = node;
        this.body = document.querySelector('body');
        this.levelTwo = document.querySelector('[data-nav-level-2]');
        this.levelThree = document.querySelector('[data-nav-level-3]');
        this.navChildren = document.querySelectorAll('[data-menu-child]');
        this.visibleClass = 'is-visible';
        this.activeClass = 'is-active';
        this.bindEventListeners();
    }

    bindEventListeners() {
        // todo - change depending on window size
        const condition = false;

        if(condition) {
            this.navChildren.forEach(child => {
                child.addEventListener('mouseover', (e) => {
                    this.activatePrevious(e.target.dataset);
                });

                child.addEventListener('mouseout', (e) => {
                    this.deactivatePrevious(e.target.dataset);
                });
            });

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
                this.levelTwo.classList.add(this.visibleClass);
                if (e.target.tagName === 'A') {
                    this.showPrevSubMenu(e.target.dataset.menu);
                }
            });

            this.levelThree.addEventListener('mouseout', (e) => {
                this.levelTwo.classList.remove(this.visibleClass);
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
        const targetMenu = document.querySelector(`[data-nav-level-2] [data-menu-${menu}]`);
        targetMenu.classList.add(this.visibleClass);
    }

    // hide level two if we leave level three
    hidePrevSubMenu(menu) {
        const targetMenu = document.querySelector(`[data-nav-level-2] [data-menu-${menu}]`);
        targetMenu.classList.remove(this.visibleClass);
    }

    toggleSubMenu(menuLevel, menu) {
        const targetMenu = document.querySelector(`[data-nav-level-${menuLevel}] [data-menu-${menu}]`);
        targetMenu.classList.contains(this.visibleClass) ? targetMenu.classList.remove(this.visibleClass) : targetMenu.classList.add(this.visibleClass);
    }

    toggleDrawer(menuLevel) {
        const drawer = document.querySelector(`[data-nav-level-${menuLevel}]`);
        drawer.classList.contains(this.visibleClass) ? drawer.classList.remove(this.visibleClass) : drawer.classList.add(this.visibleClass);
    }

    // add active link styles if we navgiate deeper into the menu
    activatePrevious(dataset) {
        const targetLevel = dataset.targetLevel;
        const menu = dataset.menu;

        const prevMenuNumber = targetLevel - 2;
        const prevMenuItem = document.querySelector(`[data-nav-level-${prevMenuNumber}] a[data-menu="${menu}"]`);
        prevMenuItem.classList.add(this.activeClass);
    }

    // add active link styles if we navgiate deeper into the menu
    deactivatePrevious(dataset) {
        const targetLevel = dataset.targetLevel;
        const menu = dataset.menu;

        const prevMenuNumber = targetLevel - 2;
        const prevMenuItem = document.querySelector(`[data-nav-level-${prevMenuNumber}] a[data-menu="${menu}"]`);
        prevMenuItem.classList.remove(this.activeClass);
    }
}

export default SubMenu;
