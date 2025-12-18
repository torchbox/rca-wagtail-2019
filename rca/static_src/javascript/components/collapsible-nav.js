class CollapsibleNav {
    static selector() {
        return '[data-collapsible-nav]';
    }

    constructor(node) {
        this.collapsibleNav = node;
        this.openCollapsibleNavButton = this.collapsibleNav.querySelector(
            '[data-open-collapsible-nav-button]',
        );
        this.closeCollapsibleNavButton = this.collapsibleNav.querySelector(
            '[data-close-collapsible-nav-button]',
        );
        this.bindEvents();
    }

    bindEvents() {
        this.openCollapsibleNavButton.addEventListener('click', () => {
            this.collapsibleNav.classList.add('is-open');
            // focus the close button
            this.closeCollapsibleNavButton.focus();
        });
        this.closeCollapsibleNavButton.addEventListener('click', () => {
            this.collapsibleNav.classList.remove('is-open');
            // focus the open button
            this.openCollapsibleNavButton.focus();
        });
    }
}

export default CollapsibleNav;
