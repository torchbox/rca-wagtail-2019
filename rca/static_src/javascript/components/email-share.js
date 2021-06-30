class EmailShare {
    static selector() {
        return '[data-email-share]';
    }

    constructor(node) {
        this.emailButton = node;
        this.bindEvents();
    }

    emailCurrentPage(event) {
        event.preventDefault();
        window.location.href = `mailto:?subject=${document.title}&body=${escape(
            window.location.href,
        )}`;
    }

    bindEvents() {
        this.emailButton.addEventListener('click', (event) =>
            this.emailCurrentPage(event),
        );
    }
}

export default EmailShare;
