import LazyLoad from 'vanilla-lazyload';

function LazyLoadImages() {
    const lazyLoadInstance = new LazyLoad({
        elements_selector: '.lazyload',
    });

    if (lazyLoadInstance) {
        lazyLoadInstance.update();
    }
}

LazyLoadImages();
