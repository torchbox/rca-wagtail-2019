class SubMenu {
    static selector() {
        return '[data-menu-parent]';
    }

    constructor(node) {
        this.node = node;
        this.navLinks = document.querySelectorAll('[data-menu-id]');
        this.visibleClass = 'is-visible';
        this.activeClass = 'is-active';
        this.bindEventListeners();
    }

    bindEventListeners() {
        this.isDesktop = window.innerWidth > 1022;

        if (this.isDesktop) {
            this.handleDesktop();
        } else {
            this.handleMobile();
        }
    }

    // Nav item text is an actual link on desktop
    // Use the icon to drill down the menu
    handleDesktop() {
        this.node.addEventListener('click', (e) => {
            if (!this.node.classList.contains('nav__link')) {
                e.preventDefault();
                this.activateMenu(e.target);
            }
        });
    }

    // Nav item text and icon used to drill down on mobile
    handleMobile() {
        this.node.addEventListener('click', (e) => {
            e.preventDefault();
            this.activateMenu(e.target);
        });
    }

    removeClass(selector, className) {
        const toRemove = document.querySelectorAll(selector);
        toRemove.forEach((item) => {
            item.classList.remove(className);
        });
        return toRemove;
    }

    addClass(selector, className) {
        const toAdd = document.querySelectorAll(selector);
        toAdd.forEach((item) => {
            item.classList.add(className);
        });
        return toAdd;
    }

    // add active link styles
    activateMenu(navItem) {
        // eslint-disable-next-line radix
        const itemLevel = parseInt(navItem.dataset.navLevel);
        const childDrawer = `[data-nav-level-${itemLevel + 1}]`;
        const grandChildDrawer = `[data-nav-level-${itemLevel + 2}]`;
        const childMenus = `[data-ul="${itemLevel + 1}"]`;

        // hide all <ul> elements in child menus
        this.removeClass(childMenus, this.visibleClass);

        // show only my child menu
        const childMenuSelector = `[data-menu-${navItem.dataset.menuId}]`;
        const childMenu = this.addClass(childMenuSelector, this.visibleClass);

        // only show child drawer if has a menu else make sure it's gone
        if (childMenu.length > 0) {
            this.addClass(childDrawer, this.visibleClass);
        } else {
            this.removeClass(childDrawer, this.visibleClass);
        }

        // ensure grandchild drawers are hidden
        this.removeClass(grandChildDrawer, this.visibleClass);

        // deactivate all sibling links
        const siblingLinks = `[data-nav-level="${itemLevel}"]`;
        this.removeClass(siblingLinks, this.activeClass);

        // deactivate all child links
        const childLinks = `[data-nav-level="${itemLevel + 1}"]`;
        this.removeClass(childLinks, this.activeClass);

        // deactive parent <li>'s
        const siblingLinkElements = document.querySelectorAll(`[data-nav-level="${itemLevel}"]`);
        siblingLinkElements.forEach(link => {
            link.parentElement.classList.remove(this.activeClass);
        });

        // activate my link
        navItem.classList.add(this.activeClass);

        // activate parent <li>
        const parentItem = navItem.parentElement;
        parentItem.classList.add(this.activeClass);

        // find <a> with same id in previous menu and activate
        const parentAnchor = document.querySelector(
            `[data-id="${navItem.dataset.parentId}"]`,
        );

        if (parentAnchor) {
            this.activatePrevious(parentAnchor);
        }
    }
}

export default SubMenu;
