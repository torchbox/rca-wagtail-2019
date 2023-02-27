import Glide from '@glidejs/glide';
import ArrowDisabler from './carousel-arrow-disabler';

class PeekCarousel {
    static selector() {
        return '[data-peek-carousel]';
    }

    constructor(node) {
        this.node = node;
        this.windowWidth = window.innerWidth;
        this.allTabs = document.querySelectorAll('[data-tab]');

        this.getMargins();
        this.createSlideshow();
        this.slideTotal = this.node.dataset.slidetotal;
        this.slideshow.mount({ ArrowDisabler });
        this.bindEvents();
        this.setLiveRegion();
    }

    bindEvents() {
        this.slideshow.on('move.after', () => {
            this.updateAriaRoles();
            this.updateLiveRegion();
        });

        window.addEventListener('resize', () => {
            // Check window width has actually changed and it's not just iOS triggering a resize event on scroll
            // eslint-disable-next-line eqeqeq
            if (window.innerWidth != this.windowWidth) {
                // Update the window width for next time
                this.windowWidth = window.innerWidth;
                this.getMargins();
                this.updateSlideshowBreakpoint();
            }
        });

        // If the carousel is hidden in a tab, it needs to be rebuilt on tab click
        this.allTabs.forEach((item) => {
            item.addEventListener('click', () => {
                this.updateSlideshowBreakpoint();
            });
        });
    }

    getMargins() {
        // Get outer grid size for peek value
        const leftEdge = document.querySelector('[data-left-edge]');
        this.leftEdgeCoords = leftEdge.getBoundingClientRect();
    }

    createSlideshow() {
        this.slideshow = new Glide(this.node, {
            type: 'slider',
            startAt: 0,
            perView: 1,
            rewind: false,
            autoplay: false,
            breakpoints: {
                598: {
                    peek: { before: 20, after: 20 },
                    gap: 20,
                },
                1022: {
                    peek: { before: 60, after: 60 },
                    gap: 0,
                },
                4000: {
                    gap: 0,
                    peek: {
                        before: this.leftEdgeCoords.right,
                        after: this.leftEdgeCoords.right,
                    },
                },
            },
        });
    }

    updateSlideshowBreakpoint() {
        this.slideshow.destroy();
        this.createSlideshow();
        this.slideTotal = this.node.dataset.slidetotal;
        this.slideshow.mount({ ArrowDisabler });
    }

    // sets aria-hidden on inactive slides
    updateAriaRoles() {
        // eslint-disable-next-line no-restricted-syntax
        for (const slide of this.node.querySelectorAll(
            '.glide__slide:not(.glide__slide--active)',
        )) {
            const inactiveSlideAnchors = slide.querySelectorAll('a');
            slide.setAttribute('aria-hidden', 'true');
            inactiveSlideAnchors.forEach(function inactiveAnchor(el) {
                el.setAttribute('tabindex', -1);
            });
        }
        const activeSlide = this.node.querySelector('.glide__slide--active');
        const activeSlideAnchors = activeSlide.querySelectorAll('a');
        activeSlide.removeAttribute('aria-hidden');
        activeSlideAnchors.forEach(function activeAnchor(el) {
            el.removeAttribute('tabindex');
        });
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

export default PeekCarousel;
