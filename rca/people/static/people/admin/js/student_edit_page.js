/* global $ */

// prettier-ignore
$(document).ready(() => {
    const $studentTitleField = $('input[id="id_title"][type="hidden"]');
    const $titleFieldPanel = $studentTitleField.closest('li.object');

    const $studentSlugField = $('input[id="id_slug"][type="hidden"]');
    const $slugFieldPanel = $studentSlugField.closest('li.object');

    if ($titleFieldPanel.length) {
        $titleFieldPanel.hide();
    }

    if ($slugFieldPanel.length) {
        $slugFieldPanel.hide();
    }
});
