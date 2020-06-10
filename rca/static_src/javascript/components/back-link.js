import ClassWatcher from './class-watcher';

class BackLink {
    static selector() {
        return '[data-subnav-back]';
    }

    constructor(node) {
        this.node = node;
        this.activeClass = 'is-visible';
        this.fadeIconClass = 'fade-icon';
        this.levelTwo = document.querySelector('[data-nav-level-2]');
        this.levelThree = document.querySelector('[data-nav-level-3]');
        this.levelTwoMenus = document.querySelectorAll('[data-nav-level-2] ul');
        this.levelThreeMenus = document.querySelectorAll(
            '[data-nav-level-3] ul',
        );
        // eslint-disable-next-line no-new
        new ClassWatcher(
            this.levelTwo,
            this.activeClass,
            this.onClassAdd.bind(this),
            this.onClassRemove.bind(this),
        );
        // eslint-disable-next-line no-new
        new ClassWatcher(
            this.levelThree,
            this.activeClass,
            this.onClassAdd.bind(this),
            this.onClassRemove.bind(this),
        );

        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('click', () => {
            // re-activate all icons
            this.removeFadeIconClass();

            // check if level 3 is open first
            if (this.levelThree.classList.contains(this.activeClass)) {
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
        menus.forEach((menu) => {
            menu.classList.remove(this.activeClass);
        });
    }

    onClassAdd() {
        this.node.classList.add(this.activeClass);
    }

    onClassRemove() {}

    removeFadeIconClass() {
        // get all the active icons
        const activeIcons = document.querySelectorAll('.fade-icon');

        // remove the class
        activeIcons.forEach((icon) => {
            icon.classList.remove(this.fadeIconClass);
        });
    }
}

export default BackLink;
