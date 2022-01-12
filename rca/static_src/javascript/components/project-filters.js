import 'intersection-observer';
import scrollama from 'scrollama';

/* eslint-disable no-restricted-syntax */
class ProjectFilters {
    static selector() {
        return '[data-filter-option]';
    }

    constructor(node) {
        // Filters
        this.filter = node;
        this.body = document.querySelector('body');
        this.filterBar = document.querySelector('[data-filter-bar]');
        this.filterBarSmall = document.querySelector('[data-filter-bar-small]');
        this.resetButton = document.querySelector('[data-filters-reset]');
        this.clearButtons = document.querySelectorAll(
            '[data-filters-clear-category]',
        );
        this.categoryButtons = document.querySelectorAll(
            '[data-project-category]',
        );
        this.formSubmit = document.querySelectorAll('[data-filter-submit]');
        this.filterContainer = document.querySelector(
            'filter-takeover__container',
        );

        // Tabs
        this.allTabs = document.querySelectorAll('[data-tab]');

        // Mobile specific
        this.mobileLauncher = document.querySelector('[data-filter-launcher]');
        this.backButtons = document.querySelectorAll('[data-filter-back]');

        // Events
        this.bindEvents();
    }

    clearCurrentCategoryFilters(tab) {
        const activeTab = document.getElementById(tab);
        const activeFilters = activeTab.querySelectorAll(
            ProjectFilters.selector(),
        );

        // Deselect all active filters in current Category
        for (const filter of activeFilters) {
            filter.classList.remove('selected');
            // Uncheck checkboxes
            filter
                .closest('.filter-tab-options__item')
                .querySelector('.filter-tab-options__checkbox').checked = false;
        }
    }

    detectPositionSticky() {
        // instantiate the scrollama
        const scroller = scrollama();

        // setup the instance, pass callback functions
        scroller
            .setup({
                step: '.js-detect-sticking',
                offset: 0.02, // 1 bottom, 0 top - set a slight offset to ensure functions are called consistently with 2 sticky elements
            })
            .onStepEnter(() => {
                this.filterBar.classList.add('filter-bar--stuck');
                this.filterBarSmall.classList.add('filter-bar--stuck');
                this.applyThemeDarkMobile();
            })
            .onStepExit(() => {
                this.filterBar.classList.remove('filter-bar--stuck');
                this.filterBarSmall.classList.remove('filter-bar--stuck');
                this.applyThemeLightMobile();
            });

        // setup resize event
        window.addEventListener('resize', scroller.resize);
    }

    CategorySelected(filter) {
        const categoryID = filter
            .closest('.js-tab-panel')
            .getAttribute('aria-labelledby');
        const currentCategory = document.getElementById(categoryID);

        this.resetButtonActive();
        currentCategory.classList.add('categories-tablist__tab--selected');
    }

    CategoryRemoveSelected(categoryID) {
        const tabID = `tab-${categoryID}`;
        const currentCategory = document.getElementById(tabID);

        currentCategory.classList.remove('categories-tablist__tab--selected');
    }

    checkCategoryActive(filter) {
        const categoryID = filter.closest('.js-tab-panel').id;
        const categoryFilters = document.querySelectorAll(
            `#${categoryID} [data-filter-option]`,
        );
        const categoryResetButton = document.querySelectorAll(
            `#${categoryID} [data-filters-clear-category]`,
        );

        // Run through all filters in active category and add selected items to array
        const selectedItems = [];

        Array.prototype.map.call(categoryFilters, (element) => {
            if (element.classList.contains('selected')) {
                selectedItems.push(element);
            }
        });

        // If no selected items remove selected category and hide clear button
        if (selectedItems.length === 0) {
            this.CategoryRemoveSelected(categoryID);

            categoryResetButton.forEach((item) => {
                item.classList.add('hidden');
            });
        } else {
            this.CategorySelected(filter);
        }

        // check for active filters
        const filtersAreActive = [...this.categoryButtons].some((button) =>
            button.classList.contains('categories-tablist__tab--selected'),
        );

        if (filtersAreActive) {
            // add active class to mobile button if so
            this.mobileLauncher.classList.add('active');
        } else {
            // remove if not
            this.mobileLauncher.classList.remove('active');
        }
    }

    checkResetStatus() {
        const selectedCategories = [];

        Array.prototype.map.call(this.categoryButtons, (element) => {
            if (
                element.classList.contains('categories-tablist__tab--selected')
            ) {
                selectedCategories.push(element);
            }
        });

        if (selectedCategories.length === 0) {
            this.resetButtonHidden();
        }
    }

    checkClearStatus() {
        const activeCategories = [];

        Array.prototype.map.call(this.categoryButtons, (element) => {
            if (
                element.classList.contains('categories-tablist__tab--selected')
            ) {
                activeCategories.push(element);
            }
        });

        activeCategories.forEach((category) => {
            const ActiveTabID = category.getAttribute('data-tab');
            const ActiveTabClearButton = document
                .getElementById(ActiveTabID)
                .querySelector('[data-filters-clear-category]');
            ActiveTabClearButton.classList.remove('hidden');
        });
    }

    applyThemeDark() {
        this.filterBar.classList.remove('bg', 'bg--light');
        this.filterBar.classList.add('bg', 'bg--dark');
    }

    applyThemeLight() {
        this.filterBar.classList.remove('bg', 'bg--dark');
        this.filterBar.classList.add('bg', 'bg--light');
    }

    applyThemeDarkMobile() {
        this.filterBarSmall.classList.remove('bg', 'bg--light');
        this.filterBarSmall.classList.add('bg', 'bg--dark');
    }

    applyThemeLightMobile() {
        this.filterBarSmall.classList.remove('bg', 'bg--dark');
        this.filterBarSmall.classList.add('bg', 'bg--light');
    }

    resetButtonActive() {
        this.resetButton.classList.remove('reset--hidden');
    }

    resetButtonHidden() {
        this.resetButton.classList.add('reset--hidden');
    }

    launchProjectFilters() {
        this.body.classList.add('no-scroll');
        this.body.classList.add('project-filters');
        this.applyThemeLight();
        // Remove to allow css to handle theme
        this.filterBar.classList.remove('filter-bar--stuck');
    }

    closeProjectFilters() {
        this.body.classList.remove('no-scroll');
        this.body.classList.remove('project-filters');
        this.applyThemeDark();
        // Check if class needs to be applied again
        this.detectPositionSticky();
    }

    // Check if an element is within a parent
    contains(parent, child) {
        return parent !== child && parent.contains(child);
    }

    bindEvents() {
        // Detect when sticky
        this.detectPositionSticky();

        // Check for existing filters on page load
        this.checkCategoryActive(this.filter);

        // If items selected then show reset
        this.checkResetStatus();

        // Check if clear needed
        this.checkClearStatus();

        // Filters
        this.filter.addEventListener('click', (e) => {
            const filterItem = e.target;
            const closestClearButton = e.currentTarget
                .closest('.filter-tab-options__container')
                .querySelector('[data-filters-clear-category]');
            if (filterItem.classList.contains('selected')) {
                filterItem.classList.remove('selected');
                this.checkCategoryActive(filterItem);
            } else {
                // If this is a single option form, then only allow a single selection for programme tab
                if (e.target.hasAttribute('data-filter-single')) {
                    const parentEl = document.querySelector('#programme');

                    if (this.contains(parentEl, e.target)) {
                        // Clear all filters selected state within current tab (programmes)
                        // Get the tab ID that clear sits within
                        const targetTabID = e.target
                            .closest(['.js-tab-panel'])
                            .getAttribute('id');
                        this.clearCurrentCategoryFilters(targetTabID);
                    }
                }
                filterItem.classList.add('selected');
                // Show reset button
                closestClearButton.classList.remove('hidden');
                this.CategorySelected(filterItem);
            }
            // Check if reset needs to show
            this.checkResetStatus();
        });

        // Categories
        this.categoryButtons.forEach((item) => {
            item.addEventListener('click', () => {
                this.launchProjectFilters();
            });
        });

        // Clear
        this.clearButtons.forEach((item) => {
            item.addEventListener('click', (e) => {
                e.preventDefault();

                // Get the tab ID that clear sits within
                const targetTabID = e.target
                    .closest(['.js-tab-panel'])
                    .getAttribute('id');

                // Clear all filters selected state
                this.clearCurrentCategoryFilters(targetTabID);

                // Unselect current catergory
                this.CategoryRemoveSelected(targetTabID);

                // Hide this clear button when clicked
                e.target.classList.add('hidden');

                // Check if reset needs to show
                this.checkResetStatus();
            });
        });

        // Reset
        this.resetButton.addEventListener('click', () => {
            this.closeProjectFilters();
        });

        // Submit
        this.formSubmit.forEach((item) => {
            item.addEventListener('click', () => {
                this.closeProjectFilters();
                this.body.classList.remove('project-filters-mobile');
            });
        });

        // Mobile launcher
        this.mobileLauncher.addEventListener('click', () => {
            // scroll user to top to reset filter theme
            document.documentElement.scrollTop = 0;
            this.body.classList.add('project-filters-mobile');
            this.body.classList.add('no-scroll');
            this.applyThemeLightMobile();
        });

        // Back
        this.backButtons.forEach((item) => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                // Get the tab ID that clear sits within
                const targetTabID = e.target
                    .closest(['.js-tab-panel'])
                    .getAttribute('id');

                // Hide current tab, and set aria selected to false
                document
                    .getElementById(targetTabID)
                    .classList.add('tabs__panel--hidden');
                document
                    .getElementById(targetTabID)
                    .setAttribute('aria-selected', 'false');

                // Deactivate filter takeover
                this.body.classList.remove('project-filters');
            });
        });

        window.addEventListener('hashchange', () => {
            // if there's no hash, reset the filters
            if (
                !window.location.hash.length > 0 ||
                window.location.hash === '#results'
            ) {
                // close filters modal
                this.closeProjectFilters();

                // hide the mobile filters
                this.body.classList.remove('project-filters-mobile');

                this.applyThemeLightMobile();

                // de-activate the filter buttons
                this.categoryButtons.forEach((button) => {
                    button.setAttribute('aria-selected', 'false');
                });
                // ensure the mobile filters menu is shown when navigating using back button
            } else if (window.location.hash === '#filters-active') {
                // Hide all tabs, and set aria-selected to false
                [...document.querySelectorAll('.js-tab-panel')].forEach(
                    (panel) => {
                        panel.classList.add('tabs__panel--hidden');
                        panel.setAttribute('aria-selected', 'false');
                    },
                );

                // Deactivate filter takeover
                this.body.classList.remove('project-filters');
            }
        });
    }
}

export default ProjectFilters;
