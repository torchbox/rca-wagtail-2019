function outdatedBanner() {
    const banner = document.querySelector('[data-outdated-banner]');

    if (!banner) {
        return;
    }

    banner.addEventListener('click', () => {
        document.querySelector('[data-outdated-banner]').style.display = 'none';
    });
}

outdatedBanner();
