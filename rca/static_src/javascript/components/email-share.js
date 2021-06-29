function emailCurrentPage() {
    window.location.href = `mailto:?subject=${document.title}&body=${escape(
        window.location.href,
    )}`;
}

document.addEventListener('DOMContentLoaded', () => {
    document
        .querySelector('[data-email-share]')
        .addEventListener('click', (e) => {
            e.preventDefault();
            emailCurrentPage();
        });
});
