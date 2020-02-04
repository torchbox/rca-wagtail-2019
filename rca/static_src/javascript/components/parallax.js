import Rellax from 'rellax';

function parallax() {
    // eslint-disable-next-line no-new
    new Rellax('[data-parallax]', {
        speed: -3,
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
