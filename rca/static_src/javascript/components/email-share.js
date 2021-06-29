function emailCurrentPage() {
    window.location.href = `mailto:?subject=${document.title}&body=${escape(
        window.location.href,
    )}`;
}

document.addEventListener('DOMContentLoaded', () => {
    // remove the hash if the modal is closed
    document
        .querySelector('[data-email-share]')
        .addEventListener('click', (e) => {
            e.preventDefault();
            emailCurrentPage();
        });
});
