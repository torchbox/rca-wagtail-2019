import LazyLoad from 'vanilla-lazyload';

function LazyLoadImages() {
    var lazyLoadInstance = new LazyLoad({
        elements_selector: '.lazyload',
    });

    if (lazyLoadInstance) {
        lazyLoadInstance.update();
    }
}

LazyLoadImages();
