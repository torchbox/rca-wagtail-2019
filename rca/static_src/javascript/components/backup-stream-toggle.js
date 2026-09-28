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
            // Removing the primary player from the DOM when the backup player is shown
            this.primaryStreamWrapper?.remove();
            this.stream.hidden = false;
            this.button.setAttribute('aria-expanded', 'true');
            this.button.hidden = true;
        });
    }
}

export default BackupStreamToggle;
