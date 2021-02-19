import MicroModal from 'micromodal'; // es6 module

MicroModal.init({
    onShow: () => {
        window.location.hash = 'modal-open';
    },
    onClose: () => {
        window.location.hash = '';
    },
    awaitOpenAnimation: false,
    awaitCloseAnimation: false,
    disableScroll: true,
});

document.addEventListener('DOMContentLoaded', () => {
    const closeModal = () => {
        const modalId = document.querySelector('[data-micromodal-trigger]')
            .dataset.micromodalTrigger;
        MicroModal.close(modalId);
    };

    const showModal = () => {
        const modalId = document.querySelector('[data-micromodal-trigger]')
            .dataset.micromodalTrigger;
        MicroModal.show(modalId);
    };

    // check for a modal
    if (
        document.body.contains(
            document.querySelector('[data-micromodal-trigger]'),
        )
    ) {
        // check if the modal should be open on page load
        if (window.location.hash && window.location.hash === '#modal-open') {
            showModal();
        }
        // close the modal if the user navigates via the back button
        window.addEventListener('hashchange', () => {
            if (!window.location.hash) {
                closeModal();
            } else if (window.location.hash === '#modal-open') {
                showModal();
            }
        });

        // remove the hash if the modal is closed
        document
            .querySelector('[data-micromodal-close]')
            .addEventListener('click', () => {
                window.location.hash = '';
            });
    }
});
