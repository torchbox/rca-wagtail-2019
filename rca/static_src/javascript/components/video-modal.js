class VideoModal {
    static selector() {
        return '[data-video-modal]';
    }

    constructor(node) {
        this.modal = node;
        this.modalOpen = this.modal.querySelector('[data-modal-open]');
        this.modalWindow = this.modal.querySelector('[data-modal-window]');
        this.modalClose = this.modal.querySelector('[data-modal-close]');
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

    bindEvents() {
        this.modalOpen.addEventListener('click', (e) => {
            e.preventDefault();

            // prevent scrolling
            this.body.classList.add(this.noScrollClass);

            // show the modal
            this.modalWindow.classList.add(this.activeClass);

            // hide the header
            this.header.classList.add(this.hiddenHeaderClass);

            // add the autoplay url to the iframe
            if (
                this.iframe.getAttribute('src') !== this.modal.dataset.embedUrl
            ) {
                this.iframe.setAttribute('src', this.modal.dataset.embedUrl);
            }
        });

        this.modalClose.addEventListener('click', (e) => {
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
        });
    }
}

export default VideoModal;
