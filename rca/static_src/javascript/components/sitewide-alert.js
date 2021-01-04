import Cookies from 'js-cookie';

class SitewideAlert {
    static selector() {
        return '[data-sitewide-alert]';
    }

    constructor(node) {
        this.node = node;
        this.closeButtons = this.node.querySelectorAll(
            '[data-sitewide-alert-close]',
        );
        this.cookieName = 'sitewide-alert';
        this.cookieValue = 'disabled';
        this.activeClass = 'sitewide-alert--active';
        this.inactiveClass = 'sitewide-alert--inactive';

        this.checkCookie();
        this.bindEvents();
    }

    checkCookie() {
        if (!this.node) {
            return;
        }

        // If alert hasn't been disabled (cookie not set)
        if (!Cookies.get(this.cookieName)) {
            this.node.classList.add(this.activeClass);
        }
    }

    disableAlert(e) {
        e.preventDefault();
        // Remove active class to hide banner
        this.node.classList.remove(this.activeClass);
        this.node.classList.add(this.inactiveClass);
        // Set cookie to disable alert for current session
        Cookies.set(this.cookieName, this.cookieValue);
    }

    bindEvents() {
        if (!this.closeButtons) {
            return;
        }

        this.closeButtons.forEach((item) => {
            item.addEventListener('click', (e) => {
                this.disableAlert(e);
            });
        });
    }
}

export default SitewideAlert;
