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
        this.noScrollClass = 'no-scroll';
        this.activeClass = 'is-open';
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

            // add the autoplay url to the iframe
            this.iframe.setAttribute('src', this.modal.dataset.embedUrl);
        });

        this.modalClose.addEventListener('click', (e) => {
            e.stopPropagation();
            e.preventDefault();

            // allow scrolling
            this.body.classList.remove(this.noScrollClass);

            // hide the modal
            this.modalWindow.classList.remove(this.activeClass);

            // stop the embed playing
            this.iframe.setAttribute('src', '');
        });
    }
}

export default VideoModal;
