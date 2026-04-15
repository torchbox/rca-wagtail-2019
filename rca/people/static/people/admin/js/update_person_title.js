/* global $ */

// prettier-ignore
$(document).ready(() => {
    const $lastNameInput = $('#id_last_name');
    const $firstNameInput = $('#id_first_name');
    const $titleInput = $('#id_title');
    const $slugInput = $('#id_slug');

    function joinFirstNameLastName() {
        const firstName = $firstNameInput.val();
        const lastName = $lastNameInput.val();
        const title = `${firstName  } ${  lastName}`;

        $slugInput.data('previous-val', $slugInput.val());
        $titleInput.data('previous-val', $titleInput.val());
        $titleInput.val(title);
        $titleInput.blur(); // Trigger slug update
    }

    $firstNameInput.on('input', () => {
        joinFirstNameLastName();
    });

    $lastNameInput.on('input', () => {
        joinFirstNameLastName();
    });
});
