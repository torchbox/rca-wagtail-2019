import MicroModal from 'micromodal'; // es6 module

// Stop videos by replacing their src
const stopAllVideos = () => {
    const iframes = document.querySelectorAll('iframe');
    iframes.forEach((i) => {
        const source = i.src;
        i.src = '';
        i.src = source;
    });
};

MicroModal.init({
    onShow: () => {
        window.location.hash = 'modal-open';
    },
    onClose: () => {
        window.history.replaceState(null, null, ' ');
        stopAllVideos();
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
        // Make sure body is scrollable when modal is closed
        const bodyStyle = document.querySelector('body').style;
        bodyStyle.removeProperty('overflow');
        bodyStyle.removeProperty('height');
    };

    const showModal = () => {
        const modalId = document.querySelector('[data-micromodal-trigger]')
            .dataset.micromodalTrigger;
        MicroModal.show(modalId);
    };

    // check for a modal hash, which allows us to auto-open the modal on page load
    if (
        document.body.contains(document.querySelector('[data-micromodal-hash]'))
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
