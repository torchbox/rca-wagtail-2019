class SubMenu {
    static selector() {
        return '[data-menu-parent]';
    }

    constructor(node) {
        this.node = node;
        this.navLinks = document.querySelectorAll('[data-menu-id]');
        this.visibleClass = 'is-visible';
        this.fadeIconClass = 'fade-icon';
        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('click', (e) => {
            // Nav item text is an actual link
            // Use the icon to drill down the menu
            if (this.node.hasAttribute('data-drill-down')) {
                e.preventDefault();
                this.activateMenu(e.target);
            }
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

    removeClassFromParent(selector, className) {
        const toRemove = document.querySelectorAll(selector);
        toRemove.forEach((item) => {
            item.parentElement.classList.remove(className);
        });
        return toRemove;
    }

    addClassToParent(selector, className) {
        const toAdd = document.querySelectorAll(selector);
        toAdd.forEach((item) => {
            item.parentElement.classList.add(className);
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

        // On desktop...
        if (window.innerWidth > 1022) {
            // ...move the focus to the fisrt <a> in a child menu that was opened
            const childMenuElement = childMenu[0];
            childMenuElement
                .querySelector('a:not(.nav__link--group-heading)')
                .focus();
        }

        // only show child drawer if has a menu else make sure it's gone
        if (childMenu.length > 0) {
            this.addClass(childDrawer, this.visibleClass);
        } else {
            this.removeClass(childDrawer, this.visibleClass);
        }

        // ensure grandchild drawers are hidden
        this.removeClass(grandChildDrawer, this.visibleClass);

        // deactivate all child links
        const childLinks = `[data-nav-level="${itemLevel + 1}"]`;

        // deactive child <li>'s and remove fade icon class
        this.removeClassFromParent(childLinks, this.fadeIconClass);

        // deactive parent <li>'s and add fade icon class
        const siblingLinkElements = `[data-nav-level="${itemLevel}"]`;
        this.addClassToParent(siblingLinkElements, this.fadeIconClass);

        // activate parent <li> and remove fade icon class
        const parentItem = navItem.parentElement;
        parentItem.classList.remove(this.fadeIconClass);

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
