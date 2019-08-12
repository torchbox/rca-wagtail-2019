import Glide from '@glidejs/glide';

class Slideshow {
    static selector() {
        return '[data-slideshow]';
    }

    constructor(node) {
        this.node = node;
        this.progressbar = this.node.querySelector('[data-scroll-progress]');
        this.windowWidth = window.innerWidth

        this.getMargins();
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
            this.updateScrollbar();
        });

        // Resize Event
        window.addEventListener('resize', () => {
            // Check window width has actually changed and it's not just iOS triggering a resize event on scroll
            if (window.innerWidth != this.windowWidth) {
                // Update the window width for next time
                this.windowWidth = window.innerWidth
                this.getMargins();
                this.updateSlideshowBreakpoint();
            }
        })
    }

    getMargins() {
        var leftEdge = document.querySelector('[data-left-edge]');
        this.leftEdgeCoords = leftEdge.getBoundingClientRect();
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
            breakpoints: {
                598: {
                    peek: { before: 20, after: 20 },
                },
                1022: {
                    peek: { before: 60, after: 60 },
                },
                4000: {
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
        this.slideshow.mount();
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

    // Update scrollbar position for mobile and tablet.
    updateScrollbar() {
        var total = this.slideTotal;
        var current = this.slideshow.index + 1; // array starts from 0 so plus 1
        var percentage = (100 / total) * current;
        var space = 100 - percentage;
        var scrollsize = 100 / total;
        this.progressbar.style.width = `${scrollsize}%`;
        this.progressbar.style.right = `${space}%`;
    }
}

export default Slideshow;
