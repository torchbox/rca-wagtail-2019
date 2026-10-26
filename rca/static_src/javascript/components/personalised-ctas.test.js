import PersonalisedCTAs from './personalised-ctas';
import CollapsibleNav from './collapsible-nav';
import CountdownCTA from './countdown-cta';
import CTATrigger from './cta-trigger';
import EmbeddedFooterCTA from './embedded-footer-cta';

jest.mock('./collapsible-nav', () => {
    const Component = jest.fn();
    Component.selector = () => '[data-collapsible-nav]';
    return Component;
});
jest.mock('./countdown-cta', () => {
    const Component = jest.fn();
    Component.selector = () => '[data-countdown-cta]';
    return Component;
});
jest.mock('./cta-trigger', () => {
    const Component = jest.fn();
    Component.selector = () => '[data-cta]';
    return Component;
});
jest.mock('./embedded-footer-cta', () => {
    const Component = jest.fn();
    Component.selector = () => '.text-teaser--footer-cta';
    return Component;
});

describe('Personalised CTAs', () => {
    beforeEach(() => {
        jest.clearAllMocks();
        document.body.innerHTML = `
            <main data-personalisation-url="/ctas-for-test-page/">
                <article>Shared page content</article>
                <div data-personalisation-slot="user"></div>
                <div data-personalisation-slot="navigation"></div>
                <div data-personalisation-slot="footer"></div>
                <div data-personalisation-slot="countdown"></div>
            </main>
        `;
        global.fetch = jest.fn();
    });

    afterEach(() => {
        delete global.fetch;
    });

    it('fetches private fragments and activates all four CTA types', async () => {
        fetch.mockResolvedValue({
            ok: true,
            text: async () => `
                <template data-personalisation-fragment="user">
                    <div data-cta data-cta-modal>Visitor popup</div>
                </template>
                <template data-personalisation-fragment="navigation">
                    <div data-collapsible-nav data-cta>Navigation</div>
                </template>
                <template data-personalisation-fragment="footer">
                    <div class="text-teaser--footer-cta">Visitor footer</div>
                </template>
                <template data-personalisation-fragment="countdown">
                    <div data-countdown-cta data-cta>Countdown</div>
                </template>
            `,
        });

        const loader = new PersonalisedCTAs(document.querySelector('main'));
        await loader.loaded;

        expect(fetch).toHaveBeenCalledTimes(1);
        expect(fetch).toHaveBeenCalledWith('/ctas-for-test-page/', {
            credentials: 'same-origin',
            cache: 'no-store',
        });
        expect(
            document.querySelector('[data-personalisation-slot="user"]'),
        ).toHaveTextContent('Visitor popup');
        expect(
            document.querySelector('[data-personalisation-slot="footer"]'),
        ).toHaveTextContent('Visitor footer');
        expect(document.querySelector('article')).toHaveTextContent(
            'Shared page content',
        );
        expect(CollapsibleNav).toHaveBeenCalledTimes(1);
        expect(CountdownCTA).toHaveBeenCalledTimes(1);
        expect(CTATrigger).toHaveBeenCalledTimes(3);
        expect(EmbeddedFooterCTA).toHaveBeenCalledTimes(1);
    });

    it('leaves the shared page usable when the request fails', async () => {
        fetch.mockRejectedValue(new Error('Network unavailable'));

        const loader = new PersonalisedCTAs(document.querySelector('main'));
        await expect(loader.loaded).resolves.toBe(false);

        expect(document.querySelector('article')).toHaveTextContent(
            'Shared page content',
        );
        expect(CTATrigger).not.toHaveBeenCalled();
    });

    it('does not insert error responses into the page', async () => {
        const text = jest.fn();
        fetch.mockResolvedValue({ ok: false, text });

        const loader = new PersonalisedCTAs(document.querySelector('main'));
        await expect(loader.loaded).resolves.toBe(false);

        expect(text).not.toHaveBeenCalled();
        expect(CTATrigger).not.toHaveBeenCalled();
    });

    it('handles empty fragments and missing slots without activating widgets', async () => {
        fetch.mockResolvedValue({
            ok: true,
            text: async () => `
                <template data-personalisation-fragment="user"></template>
                <template data-personalisation-fragment="missing">
                    <div data-cta>Unused content</div>
                </template>
            `,
        });

        const loader = new PersonalisedCTAs(document.querySelector('main'));
        await expect(loader.loaded).resolves.toBe(true);

        expect(CTATrigger).not.toHaveBeenCalled();
        expect(document.body).not.toHaveTextContent('Unused content');
    });
});
