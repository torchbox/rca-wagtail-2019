/* eslint-disable no-restricted-syntax */

class ProjectFilters {
    static selector() {
        return '[data-filter-option]';
    }

    constructor(node) {
        // Filters
        this.filter = node;
        this.filterBar = document.querySelectorAll('[data-filter-bar]');
        this.resetButton = document.querySelectorAll('[data-filters-reset]');
        this.clearButton = document.querySelectorAll(
            '[data-filters-clear-category]',
        );
        this.category = document.querySelectorAll('[data-project-category]');

        // Tabs
        this.allTabs = document.querySelectorAll('[data-tab]');

        // Events
        this.bindEvents();
    }

    launchProjectFilters() {
        document.querySelector('body').classList.add('project-filters');
    }

    closeProjectFilters() {
        document.querySelector('body').classList.remove('project-filters');
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

    bindEvents() {
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
            item.addEventListener('click', (e) => {
                e.preventDefault();
                this.launchProjectFilters();

                // Add theme colour
                for (const bar of this.filterBar) {
                    bar.classList.add('bg', 'bg--light');
                }
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

                // Reset filter bar colour
                for (const bar of this.filterBar) {
                    bar.classList.remove('bg', 'bg--light');
                }

                // Reset tab states
                for (const tab of this.allTabs) {
                    tab.classList.remove('active');
                    tab.setAttribute('aria-selected', 'false');
                }
            });
        });
    }
}

export default ProjectFilters;
