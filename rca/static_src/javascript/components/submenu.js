import hoverintent from 'hoverintent';

class SubMenu {
    static selector() {
        return '[data-menu-parent]';
    }

    constructor(node) {
        this.node = node;
        this.navLinks = document.querySelectorAll('[data-menu-id]');
        this.visibleClass = 'is-visible';
        this.activeClass = 'is-active';
        this.hoverintentOptions = { timeout: 400 };
        this.bindEventListeners();
    }

    bindEventListeners() {
        this.isDesktop = window.innerWidth > 1022;

        if (this.isDesktop) {
            this.initDesktop();
        } else {
            this.initTablet();
        }
    }

    // desktop hover events
    initDesktop() {
        this.navLinks.forEach((link) => {
            hoverintent(
                link,
                (e) => {
                    // on hover
                    this.activateMenu(e.target);
                },
                () => {
                    // hover out
                },
            ).options(this.hoverintentOptions);
        });

        // delay hover actions to make the menu more useable
        hoverintent(
            this.node,
            (e) => {
                // mouse over
                this.activateMenu(e.target);
            },
            () => {
                // mouseout
            },
        ).options(this.hoverintentOptions);
    }

    // tablet click events
    initTablet() {
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

        // activate my link
        navItem.classList.add(this.activeClass);

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
