class VideoModal {
    static selector() {
        return '[data-video-modal]';
    }

    constructor(node) {
        this.modal = node;
        this.modalOpenButton = this.modal.querySelector('[data-modal-open]');
        this.modalWindow = this.modal.querySelector('[data-modal-window]');
        this.modalCloseButton = this.modal.querySelector('[data-modal-close]');
        this.iframe = this.modal.querySelector('iframe');
        this.src = this.iframe.getAttribute('src');
        this.body = document.querySelector('body');
        this.header = document.querySelector('[data-header]');
        this.noScrollClass = 'no-scroll';
        this.activeClass = 'is-open';
        this.hiddenHeaderClass = 'app__header--hidden';
        this.storeIframeSrc();
    }

    storeIframeSrc() {
        // store the iframe src on the anchor with the autoplay param
        this.modal.setAttribute('data-embed-url', `${this.src}&autoplay=1`);

        this.bindEvents();
    }

    openModal(e) {
        e.preventDefault();

        // prevent scrolling
        this.body.classList.add(this.noScrollClass);

        // show the modal
        this.modalWindow.classList.add(this.activeClass);

        // hide the header
        this.header.classList.add(this.hiddenHeaderClass);

        // add the autoplay url to the iframe
        if (this.iframe.getAttribute('src') !== this.modal.dataset.embedUrl) {
            this.iframe.setAttribute('src', this.modal.dataset.embedUrl);
        }
    }

    closeModal(e) {
        e.stopPropagation();
        e.preventDefault();

        // allow scrolling
        this.body.classList.remove(this.noScrollClass);

        // hide the modal
        this.modalWindow.classList.remove(this.activeClass);

        // show the header
        this.header.classList.remove(this.hiddenHeaderClass);

        // stop the embed playing
        this.iframe.setAttribute('src', '');
    }

    bindEvents() {
        this.modalOpenButton.addEventListener('click', (e) => {
            this.openModal(e);
        });

        this.modalOpenButton.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.openModal(e);
            }
        });

        this.modalCloseButton.addEventListener('click', (e) => {
            this.closeModal(e);
        });
    }
}

export default VideoModal;
