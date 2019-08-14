class Tabs {
    static selector() {
        return '.js-tab-item';
    }

    constructor(node) {
        this.tab = node;
        this.tabset = this.tab.closest(['.js-tabs']);
        this.allTabs = this.tabset.querySelectorAll('.js-tab-item');
        let tabPanelId = this.tab.getAttribute('aria-controls');
        this.tabPanel = document.getElementById(tabPanelId);
        this.allTabPanels = this.tabset.querySelectorAll('.js-tab-panel');
        this.path = '';
        this.getURLHash();
        this.setActiveHashTab();
        this.bindEvents();
    }

    addURLHash(e) {
        window.location.hash = e;
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

    setActiveHashTab() {
        for (let tab of this.allTabs) {
            // Check if path hash matchs any of the tab ids
            if (this.path == tab.id) {
                this.removeActive();
                tab.classList.add('active');
                tab.setAttribute('aria-selected', 'true');
                var activePane = document.querySelector(`[aria-labelledby='${tab.id}']`);
                console.log(activePane);
                activePane.classList.remove('tabs__panel--hidden');
            }
        }
    }

    bindEvents() {
        this.tab.addEventListener('click', e => {
            e.preventDefault();
            this.removeActive();
            this.tab.classList.add('active');
            this.tab.setAttribute('aria-selected', 'true');
            this.tabPanel.classList.remove('tabs__panel--hidden');
            this.addURLHash(this.tab.id);
        });
    }
}

export default Tabs;
