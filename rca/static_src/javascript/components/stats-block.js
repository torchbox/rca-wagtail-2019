function handler(entries) {
    for (let entry of entries) {
        if (entry.isIntersecting) {
            entry.target.classList.add('section--before-fixed');
        } else {
            entry.target.classList.remove('section--before-fixed');
        }
    }
}

if (document.body.contains(document.querySelector('[data-stat-block]'))) {
    if ('IntersectionObserver' in window) {
        let observer = new IntersectionObserver(handler);
        observer.observe(document.querySelector('[data-stat-block]'));
    }
}
