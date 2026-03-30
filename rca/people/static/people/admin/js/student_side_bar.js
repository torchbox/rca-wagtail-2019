/* global $ */

// prettier-ignore
$(document).ready(() => {
    const $studentSideBar = $('aside[data-student-sidebar]');
    let $searchForm;
    if ($studentSideBar.length) {
        $searchForm = $studentSideBar.find('form[role="search"]');
        $searchForm.remove();
    }
});
