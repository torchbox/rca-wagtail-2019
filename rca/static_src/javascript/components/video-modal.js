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
        this.bindEvents();
    }

    bindEvents() {
        this.modalOpen.addEventListener('click', (e) => {
            e.preventDefault();
            this.modalWindow.classList.add('open');
            this.src += '&autoplay=1';
            this.iframe.setAttribute('src', this.src);
        });

        this.modalClose.addEventListener('click', (e) => {
            e.preventDefault();
            this.modalWindow.classList.remove('open');
        });
    }
}

export default VideoModal;
