import CollapsibleNav from './collapsible-nav';
import CountdownCTA from './countdown-cta';
import CTATrigger from './cta-trigger';
import EmbeddedFooterCTA from './embedded-footer-cta';

export const initialiseCTAComponents = (root) => {
    [CollapsibleNav, CountdownCTA, CTATrigger, EmbeddedFooterCTA].forEach(
        (Component) => {
            root.querySelectorAll(Component.selector()).forEach(
                (node) => new Component(node),
            );
        },
    );
};

class PersonalisedCTAs {
    static selector() {
        return '[data-personalisation-url]';
    }

    constructor(node) {
        this.node = node;
        this.loaded = this.load();
    }

    async load() {
        try {
            const response = await fetch(this.node.dataset.personalisationUrl, {
                credentials: 'same-origin',
                cache: 'no-store',
            });
            if (!response.ok) {
                return false;
            }

            const content = document.createElement('template');
            content.innerHTML = await response.text();
            content.content
                .querySelectorAll('template[data-personalisation-fragment]')
                .forEach((fragment) => {
                    const slot = this.node.querySelector(
                        `[data-personalisation-slot="${fragment.dataset.personalisationFragment}"]`,
                    );
                    if (slot) {
                        slot.textContent = '';
                        slot.appendChild(fragment.content.cloneNode(true));
                        initialiseCTAComponents(slot);
                    }
                });
            return true;
        } catch (error) {
            // Keep the shared page usable when personalisation is unavailable.
            return false;
        }
    }
}

export default PersonalisedCTAs;
