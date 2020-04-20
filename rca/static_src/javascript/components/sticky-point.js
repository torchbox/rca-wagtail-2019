import 'intersection-observer';
import scrollama from 'scrollama';

function scrollamaInit(position) {
    // instantiate the scrollama
    const scroller = scrollama();

    // setup the instance, pass callback functions
    scroller
        .setup({
            step: '.js-sticky-point',
            offset: position, // 1 bottom, 0 top
        })
        .onStepEnter(() => {
            document.body.classList.add('sticky-bar');
        });

    // setup resize event
    window.addEventListener('resize', scroller.resize);
}

if (
    document.body.contains(document.querySelector('.js-sticky-point--bottom'))
) {
    scrollamaInit(1);
}

if (document.body.contains(document.querySelector('.js-sticky-point--top'))) {
    scrollamaInit(0);
}
