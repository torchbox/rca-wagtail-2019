/*
    Loads the personalised CTAs for the current page.

    Pages are cached and the same for every visitor, so the CTAs come from a
    separate, uncached request (rca.personalisation.views.personalised_ctas).
    Each <template data-personalised-cta="..."> in its response is moved into
    the matching [data-personalised-cta-slot], and the CTA components are then
    started on what was inserted, as main.entry.js starts them on page load.
*/

import CollapsibleNav from './collapsible-nav';
import CountdownCTA from './countdown-cta';
import CTATrigger from './cta-trigger';
import EmbeddedFooterCTA from './embedded-footer-cta';

// In the order main.entry.js starts them.
const COMPONENTS = [
    CollapsibleNav,
    CountdownCTA,
    CTATrigger,
    EmbeddedFooterCTA,
];

class PersonalisedCTAs {
    static selector() {
        return '[data-personalised-ctas]';
    }

    constructor(node) {
        this.url = new URL(node.dataset.url, window.location.origin);
        // A superuser previews a segment with ?segment=<id> on the page.
        const segment = new URLSearchParams(window.location.search).get(
            'segment',
        );
        if (segment) {
            this.url.searchParams.set('segment', segment);
        }
        this.load();
    }

    async load() {
        let html;
        try {
            const response = await fetch(this.url, {
                credentials: 'same-origin',
                headers: { 'X-Requested-With': 'XMLHttpRequest' },
            });
            if (!response.ok) {
                return;
            }
            html = await response.text();
        } catch {
            // No CTAs is better than a broken page.
            return;
        }

        const container = document.createElement('template');
        container.innerHTML = html;
        container.content
            .querySelectorAll('template[data-personalised-cta]')
            .forEach((cta) => {
                const slot = document.querySelector(
                    `[data-personalised-cta-slot="${cta.dataset.personalisedCta}"]`,
                );
                if (!slot) {
                    return;
                }
                const nodes = [...cta.content.children];
                slot.replaceWith(cta.content);
                nodes.forEach((node) => {
                    PersonalisedCTAs.start(node);
                });
            });
    }

    static start(root) {
        COMPONENTS.forEach((Component) => {
            const selector = Component.selector();
            if (root.matches(selector)) {
                new Component(root);
            }
            root.querySelectorAll(selector).forEach((node) => {
                new Component(node);
            });
        });
    }
}

export default PersonalisedCTAs;
