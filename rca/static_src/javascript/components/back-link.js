import ClassWatcher from './class-watcher';

class BackLink {
    static selector() {
        return '[data-subnav-back]';
    }

    constructor(node) {
        this.node = node;
        this.activeClass = 'is-visible';
        this.levelTwo = document.querySelector('[data-nav-level-2]');
        this.levelThree = document.querySelector('[data-nav-level-3]');
        this.levelTwoMenus = document.querySelectorAll('[data-nav-level-2] ul');
        this.levelThreeMenus = document.querySelectorAll('[data-nav-level-3] ul');
        new ClassWatcher(this.levelTwo, this.activeClass, this.onClassAdd.bind(this), this.onClassRemove.bind(this));
        new ClassWatcher(this.levelThree, this.activeClass, this.onClassAdd.bind(this), this.onClassRemove.bind(this));

        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('click', () => {
            // check if level 3 is open first
            if(this.levelThree.classList.contains(this.activeClass)) {
                this.levelThree.classList.remove(this.activeClass);
                this.hideMenus(this.levelThreeMenus);
            } else {
                this.node.classList.remove(this.activeClass);
                this.levelTwo.classList.remove(this.activeClass);
                this.hideMenus(this.levelTwoMenus);
            }
        });
    }

    hideMenus(menus) {
        menus.forEach(menu => {
            menu.classList.remove(this.activeClass);
        });
    }

    onClassAdd() {
        this.node.classList.add(this.activeClass);
    }

    onClassRemove() {
        return;
    }
}

export default BackLink;
