import Rellax from 'rellax';

function parallax() {
    // instantiate the scrollama
    var rellax = new Rellax('[data-parallax]', {
        speed: -2,
        center: false,
        wrapper: null,
        round: true,
        vertical: true,
        horizontal: false,
    });
}

if (document.body.contains(document.querySelector('[data-parallax]'))) {
    parallax();
}
