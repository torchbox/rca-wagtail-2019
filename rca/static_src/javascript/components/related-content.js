class RelatedContent {
    static selector() {
        return '[data-related-title]';
    }

    constructor(node) {
        this.node = node;
        this.visibleClass = 'is-visible';
        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('mouseover', (e) => {
            this.updateImage(e);
        });
    }

    updateImage(e) {
        const parentGroup = e.target.dataset.parentGroup;
        const targetImage = e.target.dataset.targetImage;

        // get all the images that belong to the group
        const images = document.querySelectorAll(`[data-group="${parentGroup}"] img`);

        // hide those images
        images.forEach(image => {
            image.classList.remove(this.visibleClass);
        });

        // get the image we want
        const currentImage = document.querySelector(`[data-group="${parentGroup}"] [data-image="${targetImage}"]`);

        // show it
        currentImage.classList.add(this.visibleClass);
    }
}

export default RelatedContent;
