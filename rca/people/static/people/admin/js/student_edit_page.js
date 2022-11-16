/* eslint-disable no-var, func-names */
/* global $ */

// prettier-ignore
$(document).ready(function () {
    var $studentTitleField = $('input[id="id_title"][type="hidden"]');
    var $titleFieldPanel = $studentTitleField.closest('li.object');

    var $studentSlugField = $('input[id="id_slug"][type="hidden"]');
    var $slugFieldPanel = $studentSlugField.closest('li.object');

    if ($titleFieldPanel.length) {
        $titleFieldPanel.hide();
    }

    if ($slugFieldPanel.length) {
        $slugFieldPanel.hide();
    }
});
