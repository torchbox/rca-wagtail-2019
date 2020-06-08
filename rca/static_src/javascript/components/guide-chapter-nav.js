import 'intersection-observer';
import scrollama from 'scrollama';

class GuideChapterNav {
    static selector() {
        return '[data-guide-chapter-nav]';
    }

    constructor(node) {
        this.node = node;
        this.prevLink = this.node.querySelector(
            '[data-guide-chapter-nav-prev]',
        );
        this.nextLink = this.node.querySelector(
            '[data-guide-chapter-nav-next]',
        );

        this.bindEvents();
    }

    bindEvents() {
        this.scrollamaInit();
    }

    scrollamaInit() {
        // instantiate the scrollama
        const scroller = scrollama();

        // setup the instance, pass callback functions
        scroller
            .setup({
                step: '.anchor-heading',
                offset: 0.3,
            })
            .onStepEnter((el) => {
                // scrolling down
                if (el.direction === 'down') {
                    this.handleScrollingDownNextLink(el);
                    this.handleScrollingDownPrevLink(el);

                    // show the nav when scrolling down into the first section
                    if (el.index === 0) {
                        document.body.classList.add('is-active');
                    }
                    // scrolling up
                } else {
                    this.handleScrollingUpPrevLink(el);
                    this.handleScrollingUpNextLink(el);

                    // hide the nav when scrolling up past the first section
                    if (el.index === 0) {
                        document.body.classList.remove('is-active');
                    }
                }
            });

        // setup resize event
        window.addEventListener('resize', scroller.resize);
    }

    // Scrolling down - next link
    handleScrollingDownNextLink(el) {
        const nextSectionHeading = document.querySelector(
            `[data-scrollama-index="${el.index + 1}"]`,
        );

        // get the next section heading
        if (nextSectionHeading) {
            this.nextLink.href = `#${nextSectionHeading.id}`;
            // if there isn't one but there is a contact us section...
        } else if (document.body.contains(document.getElementById('contact'))) {
            // ...update the next link href to contact
            this.nextLink.href = `#contact`;
        }
    }

    // Scrolling down - prev link
    handleScrollingDownPrevLink(el) {
        // hide the prev link if we're on the first item
        if (el.index === 0) {
            this.prevLink.classList.remove('is-active');
        } else {
            this.prevLink.classList.add('is-active');
        }

        // get the next section heading
        const prevSectionHeading = document.querySelector(
            `[data-scrollama-index="${el.index - 1}"]`,
        );

        // update the previous link href
        if (prevSectionHeading) {
            this.prevLink.href = `#${prevSectionHeading.id}`;
        }
    }

    // Scrolling up - next link
    handleScrollingUpNextLink(el) {
        this.nextLink.href = `#${el.element.id}`;
    }

    // Scrolling up - prev link
    handleScrollingUpPrevLink(el) {
        // hide the previous link if we're on the first item
        if (el.index <= 1) {
            this.prevLink.classList.remove('is-active');
        } else {
            this.prevLink.classList.add('is-active');
        }

        // get the previous section heading
        const prevSectionHeading = document.querySelector(
            `[data-scrollama-index="${el.index - 2}"]`,
        );

        // update the previous link href
        if (prevSectionHeading) {
            this.prevLink.href = `#${prevSectionHeading.id}`;
        }
    }
}

export default GuideChapterNav;
