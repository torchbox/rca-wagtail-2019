/* eslint-disable no-var, func-names */
/* global $ */

// prettier-ignore
$(document).ready(function () {
    var $studentSideBar = $('aside[data-student-sidebar]');
    var $searchForm;
    if ($studentSideBar.length) {
        $searchForm = $studentSideBar.find('form[role="search"]');
        $searchForm.remove();
    }
});
