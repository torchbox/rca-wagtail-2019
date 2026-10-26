import simplyCountdown from 'simplycountdown.js';

import PersonalisedCTAs from './personalised-ctas';

jest.mock('simplycountdown.js', () => jest.fn());

describe('Loaded CTA interactions', () => {
    beforeEach(() => {
        sessionStorage.clear();
        window.dataLayer = [];
        global.IntersectionObserver = jest
            .fn()
            .mockImplementation((callback) => ({
                observe: () => callback([{ isIntersecting: true }]),
                disconnect: jest.fn(),
            }));
        document.body.innerHTML = `
            <main data-personalisation-url="/ctas-for-test-page/">
                <div data-personalisation-slot="user"></div>
                <div data-personalisation-slot="navigation"></div>
                <div data-personalisation-slot="countdown"></div>
                <div data-personalisation-slot="footer"></div>
            </main>
        `;
        global.fetch = jest.fn().mockResolvedValue({
            ok: true,
            text: async () => `
                <template data-personalisation-fragment="user">
                    <div id="test-popup" class="modal--cta" aria-hidden="true"
                         data-cta data-cta-modal data-cta-id="popup-1" data-cta-trigger="page_load">
                        <div role="dialog">
                            <h2 class="modal__title">Audience popup</h2>
                            <button data-cta-close data-micromodal-close>Close popup</button>
                        </div>
                    </div>
                </template>
                <template data-personalisation-fragment="navigation">
                    <div data-collapsible-nav data-cta data-cta-trigger="page_load">
                        <button data-open-collapsible-nav-button>Open navigation</button>
                        <button data-close-collapsible-nav-button>Close navigation</button>
                    </div>
                </template>
                <template data-personalisation-fragment="countdown">
                    <div class="countdown-cta" data-countdown-cta
                         data-countdown-date="2030-01-01 12:00:00"
                         data-cta data-cta-id="countdown-1" data-cta-trigger="page_load">
                        <span data-countdown-timer></span>
                        <button data-cta-close>Close countdown</button>
                    </div>
                </template>
                <template data-personalisation-fragment="footer">
                    <div class="text-teaser--footer-cta">
                        <h2 class="text-teaser__heading">Audience footer</h2>
                        <a class="text-teaser__link" href="#course">View course</a>
                    </div>
                </template>
            `,
        });
    });

    afterEach(() => {
        delete global.fetch;
        delete global.IntersectionObserver;
        sessionStorage.clear();
    });

    it('preserves modal, navigation, countdown, dismissal and analytics behaviour', async () => {
        const loader = new PersonalisedCTAs(document.querySelector('main'));
        await expect(loader.loaded).resolves.toBe(true);

        const popup = document.querySelector('#test-popup');
        expect(popup).toHaveAttribute('aria-hidden', 'false');
        popup.querySelector('[data-cta-close]').click();
        expect(popup).toHaveAttribute('aria-hidden', 'true');
        expect(sessionStorage.getItem('cta_dismissed_popup-1')).toBe('1');

        const navigation = document.querySelector('[data-collapsible-nav]');
        navigation.querySelector('[data-open-collapsible-nav-button]').click();
        expect(navigation).toHaveClass('is-open');
        navigation.querySelector('[data-close-collapsible-nav-button]').click();
        expect(navigation).not.toHaveClass('is-open');

        const countdown = document.querySelector('[data-countdown-cta]');
        expect(simplyCountdown).toHaveBeenCalled();
        expect(countdown).toHaveClass('is-visible');
        countdown.querySelector('[data-cta-close]').click();
        expect(countdown).not.toHaveClass('is-visible');
        expect(sessionStorage.getItem('cta_dismissed_countdown-1')).toBe('1');

        document.querySelector('.text-teaser__link').click();
        expect(window.dataLayer).toEqual(
            expect.arrayContaining([
                expect.objectContaining({
                    event: 'popup_cta',
                    feature_activity: 'shown',
                }),
                expect.objectContaining({
                    event: 'popup_cta',
                    feature_activity: 'closed',
                }),
                expect.objectContaining({
                    event: 'navigation_prompt',
                    feature_activity: 'clicked',
                }),
                expect.objectContaining({
                    event: 'countdown_banner',
                    feature_activity: 'shown',
                }),
                expect.objectContaining({
                    event: 'embedded_component',
                    feature_activity: 'shown',
                }),
                expect.objectContaining({
                    event: 'embedded_component',
                    feature_activity: 'cta_link_click',
                }),
            ]),
        );
    });
});
