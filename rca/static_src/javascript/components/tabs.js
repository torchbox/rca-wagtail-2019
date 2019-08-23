class Tabs {
    static selector() {
        return '.js-tab-item';
    }

    constructor(node) {
        this.tab = node;
        this.tabset = this.tab.closest(['.js-tabs']);
        this.allTabs = this.tabset.querySelectorAll('.js-tab-item');
        this.allTabPanels = this.tabset.querySelectorAll('.js-tab-panel');
        this.path = '';
        this.setActiveHashTab();
        this.bindEvents();
    }

    getURLHash() {
        this.path = window.location.href.split('#')[1];
    }

    removeActive() {
        for (let tab of this.allTabs) {
            tab.classList.remove('active');
            tab.setAttribute('aria-selected', 'false');
        }

        for (let tabPanel of this.allTabPanels) {
            tabPanel.classList.add('tabs__panel--hidden');
        }
    }

    removeHeadroomPinned() {
        // ensure tab anchors are in correct place when tabs are clicked
        document.querySelector('body').classList.remove('headroom--pinned');
    }

    setActiveHashTab() {
        this.getURLHash();

        for (let tabPane of this.allTabPanels) {
            // Check if path hash matchs any of the tab ids
            if (this.path == tabPane.id) {
                var targetPanel = document.getElementById(this.path);
                var targetTab = document.querySelector(
                    `[data-tab='${this.path}']`,
                );
                this.removeActive();
                targetTab.classList.add('active');
                targetPanel.classList.remove('tabs__panel--hidden');
            }
        }
    }

    bindEvents() {
        this.tab.addEventListener('click', (e) => {
            e.preventDefault();
            var panelID = e.target.dataset.tab;
            var targetPanel = document.getElementById(panelID);
            this.removeActive();
            this.tab.classList.add('active');
            targetPanel.classList.remove('tabs__panel--hidden');
            targetPanel.setAttribute('aria-selected', 'true');
            this.removeHeadroomPinned();
            targetPanel.scrollIntoView();
        });
    }
}

export default Tabs;
