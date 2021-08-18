/* eslint-disable no-restricted-syntax */
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
                }
            });
        }
    }
}

export default Tabs;
