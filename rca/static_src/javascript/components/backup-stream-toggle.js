class BackupStreamToggle {
    static selector() {
        return '[data-backup-stream-toggle]';
    }

    constructor(node) {
        this.button = node;
        this.stream = document.getElementById(
            this.button.getAttribute('aria-controls'),
        );
        this.primaryStreamWrapper = this.button
            .closest('.streamfield-video')
            ?.querySelector('[data-primary-stream]');
        this.bindEvents();
    }

    bindEvents() {
        this.button.addEventListener('click', () => {
            // Removing the primary player from the DOM (rather than pausing
            // it via the video.js API) reliably stops playback regardless of
            // how video.js/the IVS tech restructures the element internally.
            this.primaryStreamWrapper?.remove();

            this.stream.hidden = false;
            this.button.setAttribute('aria-expanded', 'true');
            this.button.hidden = true;
        });
    }
}

export default BackupStreamToggle;
