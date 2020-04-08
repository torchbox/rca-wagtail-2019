import 'intersection-observer';
import scrollama from 'scrollama';

function scrollamaInit() {
    // instantiate the scrollama
    const scroller = scrollama();

    // setup the instance, pass callback functions
    scroller
        .setup({
            step: '.js-sticky-point',
            offset: '1', // bottom
        })
        .onStepEnter(() => {
            document.body.classList.add('sticky-bar');
        })
        .onStepExit(() => {
            document.body.classList.remove('sticky-bar');
        });

    // setup resize event
    window.addEventListener('resize', scroller.resize);
}

if (document.body.contains(document.querySelector('.js-sticky-point'))) {
    scrollamaInit();
}
