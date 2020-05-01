import Headroom from 'headroom.js';

function StartStickyHeader(offset) {
    const elem = document.body;

    const options = {
        offset,
        tolerance: {
            up: 10,
            down: 20,
        },
        classes: {
            // when element is initialised
            initial: 'headroom',
            // when scrolling up
            pinned: 'headroom--pinned',
            // when scrolling down
            unpinned: 'headroom--unpinned',
            // when above offset
            top: 'headroom--top',
            // when below offset
            notTop: 'headroom--not-top',
            // when at bottom of scoll area
            bottom: 'headroom--bottom',
            // when not at bottom of scroll area
            notBottom: 'headroom--not-bottom',
        },
    };

    const headroom = new Headroom(elem, options);
    headroom.init();
}

function StickyHeader() {
    const intViewportHeight = window.innerHeight;
    const offSetAdjuster = 60;
    const customOffet = intViewportHeight + offSetAdjuster;

    if (document.body.contains(document.querySelector('.app--homepage'))) {
        StartStickyHeader(customOffet);
    } else if (document.body.contains(document.querySelector('.no-hero'))) {
        // If no hero, sticky header needs to disapear faster, otherwise overlaps content
        StartStickyHeader(80);
    } else {
        StartStickyHeader(200);
    }
}

StickyHeader();
