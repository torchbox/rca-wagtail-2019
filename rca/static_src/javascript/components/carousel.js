import Glide from '@glidejs/glide';

class Carousel {
    static selector() {
        return '[data-carousel]';
    }

    constructor(node) {
        this.node = node;

        this.createSlideshow();
        this.slideTotal = this.node.dataset.slidetotal;
        this.bindEvents();
        this.slideshow.mount();
        this.setLiveRegion();
    }

    bindEvents() {
        this.slideshow.on('move.after', () => {
            this.updateAriaRoles();
            this.updateLiveRegion();
        });
    }

    createSlideshow() {
        this.slideshow = new Glide(this.node, {
            type: 'slider',
            startAt: 0,
            gap: 0,
            keyboard: true,
            perTouch: 1,
            touchRatio: 0.5,
            perView: 1,
            rewind: false,
            autoplay: false,
        });
    }

    // sets aria-hidden on inactive slides
    updateAriaRoles() {
        // eslint-disable-next-line no-restricted-syntax
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
        this.node.querySelector(
            '[data-liveregion]',
        ).textContent = `Item ${this.slideshow.index} of ${this.slideTotal}`;
    }
}

export default Carousel;
