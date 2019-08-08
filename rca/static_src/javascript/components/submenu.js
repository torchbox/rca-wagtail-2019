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
        this.isDesktop = window.innerWidth > 1022;

        if(this.isDesktop) {
            this.initDesktop();
        } else {
            this.initTablet();
        }
    }

    // desktop hover events
    initDesktop() {
        // level two and three event listeners
        this.navChildren.forEach(child => {
            // on hover
            child.addEventListener('mouseover', (e) => {
                // activate previous menu item
                this.activatePrevious(e.target.dataset);
            });

            // hover off
            child.addEventListener('mouseout', (e) => {
                // deactivate previous menu item
                this.deactivatePrevious(e.target.dataset);
            });
        });

        // on hover
        this.node.addEventListener('mouseover', (e) => {
            if (e.target.tagName === 'A') {
                // get matching child menu
                this.getMenuContext(e.target.dataset);
            }
        });

        // hover off
        this.node.addEventListener('mouseout', (e) => {
            if (e.target.tagName === 'A') {
                this.getMenuContext(e.target.dataset);
            }
        });

        // level three hover
        this.levelThree.addEventListener('mouseover', (e) => {
            this.levelTwo.classList.add(this.visibleClass);
            if (e.target.tagName === 'A') {
                this.showPrevSubMenu(e.target.dataset.menu);
            }
        });

        // level three hover off
        this.levelThree.addEventListener('mouseout', (e) => {
            this.levelTwo.classList.remove(this.visibleClass);
            if (e.target.tagName === 'A') {
                this.hidePrevSubMenu(e.target.dataset.menu);
            }
        });
    }

    // tablet click events
    initTablet() {
        this.node.addEventListener('click', (e) => {
            e.preventDefault();
            this.getMenuContext(e.target.dataset);
        });
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

    // hide/show a menu
    toggleSubMenu(menuLevel, menu) {
        const targetMenu = document.querySelector(`[data-nav-level-${menuLevel}] [data-menu-${menu}]`);
        targetMenu.classList.contains(this.visibleClass) ? targetMenu.classList.remove(this.visibleClass) : targetMenu.classList.add(this.visibleClass);
    }

    // hide show a drawer, containing the menus
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
