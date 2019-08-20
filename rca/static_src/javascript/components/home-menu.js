import 'intersection-observer';
import scrollama from 'scrollama';

function scrollamaInit() {
    // instantiate the scrollama
    const scroller = scrollama();

    // setup the instance, pass callback functions
    scroller
        .setup({
            step: '.js-menu-on',
            offset: '0.1',
        })
        .onStepEnter(() => {
            document.body.classList.remove('show-nav');
        })
        .onStepExit(() => {
            document.body.classList.add('show-nav');
        });

    // setup resize event
    window.addEventListener('resize', scroller.resize);
}

if (document.body.contains(document.querySelector('.js-menu-on'))) {
    scrollamaInit();
}
