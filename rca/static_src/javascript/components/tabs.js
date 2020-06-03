/* eslint-disable no-restricted-syntax */
import 'intersection-observer';
import scrollama from 'scrollama';

class Tabs {
    static selector() {
        return '.js-tab-item';
    }

    constructor(node) {
        this.tab = node;
        this.tabset = this.tab.closest(['.js-tabs']);
        this.allTabs = this.tabset.querySelectorAll('.js-tab-item');
        this.allTabPanels = this.tabset.querySelectorAll('.js-tab-panel');
        this.filterBar = document.querySelector('[data-filter-bar]');
        this.filterBarSmall = document.querySelector('[data-filter-bar-small]');
        this.categoryButtons = document.querySelectorAll(
            '[data-project-category]',
        );
        this.path = '';

        if (this.tabset.hasAttribute('data-tab-hash')) {
            this.setActiveHashTab();
        }

        this.bindEvents();
    }

    getURLHash() {
        // eslint-disable-next-line prefer-destructuring
        this.path = window.location.href.split('#')[1];
    }

    removeActive() {
        for (const tab of this.allTabs) {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        }

        for (const tabPanel of this.allTabPanels) {
            tabPanel.classList.add('tabs__panel--hidden');
            tabPanel.setAttribute('aria-selected', 'false');
        }
    }

    removeHeadroomPinned() {
        // ensure tab anchors are in correct place when tabs are clicked
        document.querySelector('body').classList.remove('headroom--pinned');
    }

    setActiveHashTab() {
        this.getURLHash();

        for (const tabPane of this.allTabPanels) {
            // Check if path hash matchs any of the tab ids
            // eslint-disable-next-line eqeqeq
            if (this.path == tabPane.id) {
                const targetPanel = document.getElementById(this.path);
                const targetTab = document.querySelector(
                    `[data-tab='${this.path}']`,
                );
                this.removeActive();
                targetTab.setAttribute('aria-selected', 'true');
                targetTab.classList.add('active');
                targetPanel.classList.remove('tabs__panel--hidden');
                targetPanel.setAttribute('aria-selected', 'true');
            }
        }
    }

    bindEvents() {
        this.tab.addEventListener('click', (e) => {
            e.preventDefault();
            const panelID = e.target.dataset.tab;
            const targetPanel = document.getElementById(panelID);
            window.location.hash = panelID;
            this.removeActive();
            e.target.setAttribute('aria-selected', 'true');
            this.tab.classList.add('active');
            targetPanel.classList.remove('tabs__panel--hidden');
            targetPanel.setAttribute('aria-selected', 'true');
            this.removeHeadroomPinned();
            targetPanel.scrollIntoView();
        });

        // used on pages with filters (project and staff picker)
        if (document.body.contains(this.filterBar)) {
            // listen for hash changes in the url to keep track when using back button
            window.addEventListener('hashchange', () => {
                // activate tab if there's a hash in the url and it's not results
                if (
                    window.location.hash &&
                    window.location.hash !== '#results'
                ) {
                    this.setActiveHashTab();
                } else {
                    // clsoe filters modal
                    document.body.classList.remove(
                        'no-scroll',
                        'project-filters',
                    );

                    // update the theme
                    this.filterBar.classList.remove('bg', 'bg--light');
                    this.filterBar.classList.add('bg', 'bg--dark');

                    // check if the has scrolled and apply relevant classes
                    this.detectPositionSticky();

                    // de-activate the filter buttons
                    this.categoryButtons.forEach((button) => {
                        button.setAttribute('aria-selected', 'false');
                    });
                }
            });
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

    applyThemeDarkMobile() {
        this.filterBarSmall.classList.remove('bg', 'bg--light');
        this.filterBarSmall.classList.add('bg', 'bg--dark');
    }

    applyThemeLightMobile() {
        this.filterBarSmall.classList.remove('bg', 'bg--dark');
        this.filterBarSmall.classList.add('bg', 'bg--light');
    }
}

export default Tabs;
