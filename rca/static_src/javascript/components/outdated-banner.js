function outdatedBanner() {
    document
        .querySelector('[data-outdated-banner-close]')
        .addEventListener('click', function() {
            document.querySelector('[data-outdated-banner]').style.display =
                'none';
        });
}

outdatedBanner();
