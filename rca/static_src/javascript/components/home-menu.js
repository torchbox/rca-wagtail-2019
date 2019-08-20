import 'intersection-observer';
import scrollama from 'scrollama';

function scrollamaInit() {
    // instantiate the scrollama
    const scroller = scrollama();

    // setup the instance, pass callback functions
    scroller
    .setup({
        step: '.js-menu-on',
        offset: '0'
    })
    .onStepEnter(response => {
        { direction: 'up' }
        document.body.classList.remove('show-nav');
    })
    .onStepExit(response => {
        { direction: 'down' }
        document.body.classList.add('show-nav');
    });

    // setup resize event
    window.addEventListener('resize', scroller.resize);
}

scrollamaInit();
