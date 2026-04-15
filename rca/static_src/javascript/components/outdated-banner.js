function outdatedBanner() {
    const banner = document.querySelector('[data-outdated-banner]');
    const bannerClose = document.querySelector('[data-outdated-banner-close]');

    if (!banner || !bannerClose) {
        return;
    }

    bannerClose.addEventListener('click', () => {
        banner.style.display = 'none';
    });
}

outdatedBanner();
