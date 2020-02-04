function outdatedBanner() {
    document
        .querySelector('[data-outdated-banner-close]')
        .addEventListener('click', () => {
            document.querySelector('[data-outdated-banner]').style.display =
                'none';
        });
}

outdatedBanner();
