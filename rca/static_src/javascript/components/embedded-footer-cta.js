class EmbeddedFooterCTA {
    static selector() {
        return '.text-teaser--footer-cta';
    }

    constructor(node) {
        this.node = node;
        this.heading = this.node.querySelector('.text-teaser__heading');
        this.ctaLink = this.node.querySelector('.text-teaser__link');

        this.trackShown();
        this.bindEvents();
    }

    trackShown() {
        const componentTitle = this.heading?.textContent.trim() || '';

        window.dataLayer = window.dataLayer || [];
        window.dataLayer.push({
            event: 'embedded_component',
            feature_activity: 'shown',
            component_title: componentTitle,
        });
    }

    bindEvents() {
        if (!this.ctaLink) {
            return;
        }

        this.ctaLink.addEventListener('click', () => {
            const buttonText =
                this.ctaLink
                    .querySelector('.link__label')
                    ?.textContent.trim() || this.ctaLink.textContent.trim();
            const componentTitle = this.heading?.textContent.trim() || '';

            window.dataLayer = window.dataLayer || [];
            window.dataLayer.push({
                event: 'embedded_component',
                feature_activity: 'cta_link_click',
                button_text: buttonText,
                component_title: componentTitle,
            });
        });
    }
}

export default EmbeddedFooterCTA;
