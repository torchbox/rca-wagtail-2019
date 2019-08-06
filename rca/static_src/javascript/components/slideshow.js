import Glide from '@glidejs/glide';

class Slideshow {
    static selector() {
        return '[data-slideshow]';
    }

    constructor(node) {
        this.node = node;
        this.slideTotal = this.node.dataset.slidetotal;

        this.slideshow = new Glide(node, {
            type: 'slider',
            startAt: 0,
            gap: 0,
            keyboard: true,
            perView: 1,
            rewind: false,
            peek: { before: 200, after: 50 },
            autoplay: false
        });

        this.slideshow.mount();
        this.bindEvents();
        this.setLiveRegion();
    }

    bindEvents() {
        this.slideshow.on('move.after', () => {
            this.updateAriaRoles();
            this.updateLiveRegion();
        });
    }

    // sets aria-hidden on inactive slides
    updateAriaRoles() {
        for (const slide of this.node.querySelectorAll(
            '.glide__slide:not(.glide__slide--active)',
        )) {
            slide.setAttribute('aria-hidden', 'true');
            slide.setAttribute('tab-index', 0);
        }
        const activeSlide = this.node.querySelector('.glide__slide--active');
        activeSlide.removeAttribute('aria-hidden');
    }

    // Sets a live region. This will announce which slide is showing to screen readers when previous / next buttons clicked
    setLiveRegion() {
        const controls = this.node.querySelector('[data-glide-el="controls"]');
        const liveregion = document.createElement('div');
        liveregion.setAttribute('aria-live', 'polite');
        liveregion.setAttribute('aria-atomic', 'true');
        liveregion.setAttribute('class', 'slideshow__liveregion');
        liveregion.setAttribute('data-liveregion', true);
        controls.appendChild(liveregion);
    }

    // Update the live region that announces the next slide.
    updateLiveRegion() {
        this.node.querySelector('[data-liveregion]').textContent =
            'Item ' + this.slideshow.index + ' of ' + this.slideTotal;
    }
}

export default Slideshow;
