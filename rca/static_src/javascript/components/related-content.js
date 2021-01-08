class RelatedContent {
    static selector() {
        return '[data-related-title]';
    }

    constructor(node) {
        this.node = node;
        this.nodeContainer = node.closest('[data-group]');
        this.visibleClass = 'is-visible';
        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('mouseover', (e) => {
            this.updateImage(e);
        });
    }

    updateImage(e) {
        const { parentGroup } = e.target.dataset;
        const { targetImage } = e.target.dataset;

        // get all the images that belong to the group
        const images = this.nodeContainer.querySelectorAll(
            `[data-group="${parentGroup}"] img`,
        );

        // hide those images
        images.forEach((image) => {
            image.classList.remove(this.visibleClass);
        });

        // get the image we want
        const currentImage = this.nodeContainer.querySelector(
            `[data-group="${parentGroup}"] [data-image="${targetImage}"]`,
        );

        // show it
        currentImage.classList.add(this.visibleClass);
    }
}

export default RelatedContent;
