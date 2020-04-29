import { disableBodyScroll, enableBodyScroll } from 'body-scroll-lock';
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
        this.resetButton = document.querySelector('[data-filters-reset]');
        this.clearButtons = document.querySelectorAll(
            '[data-filters-clear-category]',
        );
        this.categoryButtons = document.querySelectorAll(
            '[data-project-category]',
        );
        this.formSubmit = document.querySelectorAll('[data-filter-submit]');

        // Tabs
        this.allTabs = document.querySelectorAll('[data-tab]');

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
        }
    }

    detectPositionSticky() {
        // instantiate the scrollama
        const scroller = scrollama();

        // setup the instance, pass callback functions
        scroller
            .setup({
                step: '.js-detect-sticking',
                offset: 0, // 1 bottom, 0 top
            })
            .onStepEnter(() => {
                this.filterBar.classList.add('filter-bar--stuck');
            })
            .onStepExit(() => {
                this.filterBar.classList.remove('filter-bar--stuck');
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

    applyThemeDark() {
        this.filterBar.classList.remove('bg', 'bg--light');
        this.filterBar.classList.add('bg', 'bg--dark');
    }

    applyThemeLight() {
        this.filterBar.classList.remove('bg', 'bg--dark');
        this.filterBar.classList.add('bg', 'bg--light');
    }

    resetButtonActive() {
        this.resetButton.classList.remove('reset--hidden');
    }

    resetButtonHidden() {
        this.resetButton.classList.add('reset--hidden');
    }

    launchProjectFilters() {
        disableBodyScroll(this.body);
        this.body.classList.add('project-filters');
        this.applyThemeLight();
        // Remove to allow css to handle theme
        this.filterBar.classList.remove('filter-bar--stuck');
    }

    closeProjectFilters() {
        enableBodyScroll(this.body);
        this.body.classList.remove('project-filters');
        this.applyThemeDark();
        // Check if class needs to be applied again
        this.detectPositionSticky();
    }

    bindEvents() {
        // Detect when sticky
        this.detectPositionSticky();

        // Filters
        this.filter.addEventListener('click', (e) => {
            e.preventDefault();
            const filterItem = e.target;
            const closestClearButton = e.currentTarget
                .closest('.filter-tab-options__content')
                .querySelector('[data-filters-clear-category]');
            if (filterItem.classList.contains('selected')) {
                filterItem.classList.remove('selected');
                this.checkCategoryActive(filterItem);
            } else {
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
        this.resetButton.addEventListener('click', (e) => {
            e.preventDefault();
            this.closeProjectFilters();
        });

        // Submit
        this.formSubmit.forEach((item) => {
            item.addEventListener('click', () => {
                this.closeProjectFilters();
            });
        });
    }
}

export default ProjectFilters;
