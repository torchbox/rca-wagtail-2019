import 'intersection-observer';
import scrollama from 'scrollama';

class AnchorNav {
    static selector() {
        return '[data-anchor-nav]';
    }

    constructor(node) {
        this.node = node;
        this.allLinks = this.node.querySelectorAll('a[href^="#"]');
        this.scrollamaInit();
    }

    scrollamaInit() {
        // instantiate the scrollama
        const scroller = scrollama();

        // setup the instance, pass callback functions
        scroller
            .setup({
                step: '.anchor-heading',
                offset: 0.5,
            })
            .onStepEnter((el) => {
                if (el.direction === 'down') {
                    this.handleDown(el);
                }
            })
            .onStepExit((el) => {
                if (el.direction === 'up') {
                    this.handleUp(el);
                }
            });

        // setup resize event
        window.addEventListener('resize', scroller.resize);
    }

    handleDown(el) {
        // reset menu items
        this.stripClasses();

        // find the anchor link in the menu based on what was scrolled to
        const linkToActivate = document.querySelector(
            `[href="#${el.element.id}"]`,
        );

        // if there's a link add an active class
        if (linkToActivate) {
            linkToActivate.classList.add('is-active');
        }
    }

    handleUp(el) {
        // reset menu items
        this.stripClasses();

        // on scrolling up, find the previous section
        const previousSection = document.querySelector(
            `[data-scrollama-index="${el.index - 1}"]`,
        );

        // if there's a link add an active class
        if (previousSection) {
            const linkToActivate = document.querySelector(
                `[href="#${previousSection.id}"]`,
            );
            linkToActivate.classList.add('is-active');
        }
    }

    stripClasses() {
        this.allLinks.forEach((link) => link.classList.remove('is-active'));
    }
}

export default AnchorNav;
