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
        this.resetButton = document.querySelectorAll('[data-filters-reset]');
        this.clearButton = document.querySelectorAll(
            '[data-filters-clear-category]',
        );
        this.category = document.querySelectorAll('[data-project-category]');
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

    applyThemeDark() {
        this.filterBar.classList.remove('bg', 'bg--light');
        this.filterBar.classList.add('bg', 'bg--dark');
    }

    applyThemeLight() {
        this.filterBar.classList.remove('bg', 'bg--dark');
        this.filterBar.classList.add('bg', 'bg--light');
    }

    launchProjectFilters() {
        disableBodyScroll(this.body);
        this.body.classList.add('project-filters');
        this.applyThemeLight();
    }

    closeProjectFilters() {
        enableBodyScroll(this.body);
        this.body.classList.remove('project-filters');
        this.applyThemeDark();
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
            } else {
                filterItem.classList.add('selected');
                // Show reset button
                closestClearButton.classList.remove('hidden');
            }
        });

        // Categories
        this.category.forEach((item) => {
            item.addEventListener('click', () => {
                this.launchProjectFilters();
            });
        });

        // Clear
        this.clearButton.forEach((item) => {
            item.addEventListener('click', (e) => {
                e.preventDefault();

                // Get the tab ID that clear sits within
                const targetTabID = e.target
                    .closest(['.js-tab-panel'])
                    .getAttribute('id');

                // Clear all filters selected state
                this.clearCurrentCategoryFilters(targetTabID);

                // Hide this clear button when clicked
                e.target.classList.add('hidden');
            });
        });

        // Reset
        this.resetButton.forEach((item) => {
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeProjectFilters();

                // Reset tab states
                for (const tab of this.allTabs) {
                    tab.classList.remove('active');
                    tab.setAttribute('aria-selected', 'false');
                }
            });
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
