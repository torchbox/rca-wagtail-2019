import Glide from '@glidejs/glide';

class Carousel {
    static selector() {
        return '[data-carousel]';
    }

    constructor(node) {
        this.node = node;
        this.slideTotal = this.node.dataset.slidetotal;

        this.carousel = new Glide(node, {
            type: 'carousel',
            startAt: 0,
            perView: 3,
            peek: 100,
            autoplay: 2000,
            hoverpause: true, // keep this for accessibility if using autoplay
            breakpoints: {
                768: {
                    perView: 1,
                    peek: 0,
                },
            },
        });

        this.carousel.mount();
        this.bindEvents();
        this.setLiveRegion();
    }

    bindEvents() {
        this.carousel.on('move.after', () => {
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
        liveregion.setAttribute('class', 'carousel__liveregion');
        liveregion.setAttribute('data-liveregion', true);
        controls.appendChild(liveregion);
    }

    // Update the live region that announces the next slide.
    updateLiveRegion() {
        this.node.querySelector('[data-liveregion]').textContent =
            'Item ' + this.carousel.index + ' of ' + this.slideTotal;
    }
}

export default Carousel;
