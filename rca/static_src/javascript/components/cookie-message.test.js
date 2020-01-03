/* eslint-disable no-new */
import Cookies from 'js-cookie';
import CookieWarning from './cookie-message';

describe('CookieWarning', () => {
    beforeEach(() => {
        document.body.innerHTML =
            '<div class="cookie" data-cookie-message><button data-cookie-dismiss>Dismiss</button></div>';
        Cookies.remove('client-cookie');
    });

    it('gracefully fails to render for missing element', () => {
        expect(() => {
            document.body.innerHTML = '';
            new CookieWarning(document.querySelector('[data-missing]'));
        }).not.toThrowError();
    });

    it('becomes active on init', () => {
        new CookieWarning(document.querySelector(CookieWarning.selector()));
        expect(document.querySelector('[data-cookie-message]').className).toBe(
            'cookie active',
        );
    });

    it('does not activate if cookie is set', () => {
        Cookies.set('client-cookie', 'agree to cookies');

        new CookieWarning(document.querySelector(CookieWarning.selector()));
        expect(document.querySelector('[data-cookie-message]').className).toBe(
            'cookie',
        );
    });

    it('can be dismissed', () => {
        new CookieWarning(document.querySelector(CookieWarning.selector()));
        expect(document.querySelector('[data-cookie-message]').className).toBe(
            'cookie active',
        );

        const dismiss = document.querySelector('[data-cookie-dismiss]');

        dismiss.dispatchEvent(new Event('click'));

        expect(document.querySelector('[data-cookie-message]').className).toBe(
            'cookie inactive',
        );
        expect(Cookies.get('client-cookie')).toBe('agree to cookies');
    });
});
