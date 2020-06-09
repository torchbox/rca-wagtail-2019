import MicroModal from 'micromodal'; // es6 module

MicroModal.init({
    onShow: () => {window.location.hash = 'modal-open'},
    onClose: () => {window.location.hash = ''},
    awaitOpenAnimation: true,
    awaitCloseAnimation: true,
    disableScroll: true,
});

// check if the modal should be open on page load
window.onload = () => {
    if (window.location.hash && window.location.hash === '#modal-open') {
        const modalId = document.querySelector('[data-micromodal-trigger]').dataset.micromodalTrigger;
        MicroModal.show(modalId);
    }
}
