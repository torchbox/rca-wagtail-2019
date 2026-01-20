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
        this.navLinks = this.collapsibleNav.querySelectorAll(
            '.collapsible-nav__link',
        );
        this.bindEvents();
    }

    bindEvents() {
        this.openCollapsibleNavButton.addEventListener('click', () => {
            this.collapsibleNav.classList.add('is-open');
            // focus the close button
            this.closeCollapsibleNavButton.focus();

            // Track open event in dataLayer
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                event: 'navigation_prompt',
                feature_activity: 'clicked',
            });
        });

        this.closeCollapsibleNavButton.addEventListener('click', () => {
            this.collapsibleNav.classList.remove('is-open');
            // focus the open button
            this.openCollapsibleNavButton.focus();

            // Track close event in dataLayer
            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                event: 'navigation_prompt',
                feature_activity: 'closed',
            });
        });

        // Track clicks on navigation links
        this.navLinks.forEach((link) => {
            link.addEventListener('click', () => {
                const linkLabel =
                    link.querySelector('.link__label')?.textContent ||
                    link.textContent.trim();

                // Track menu item click in dataLayer
                window.dataLayer = window.dataLayer || [];
                window.dataLayer.push({
                    event: 'navigation_prompt',
                    feature_activity: 'menu_item_click',
                    menu_item: linkLabel,
                });
            });
        });
    }
}

export default CollapsibleNav;
