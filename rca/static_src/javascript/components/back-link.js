import ClassWatcher from './class-watcher';

class BackLink {
    static selector() {
        return '[data-subnav-back]';
    }

    constructor(node) {
        this.node = node;
        this.activeClass = 'is-visible';
        this.levelTwo = document.querySelector('[data-nav-level-two]');
        this.levelThree = document.querySelector('[data-nav-level-three]');
        new ClassWatcher(this.levelTwo, this.activeClass, this.onClassAdd.bind(this), this.onClassRemoval);
        new ClassWatcher(this.levelThree, this.activeClass, this.onClassAdd.bind(this), this.onClassRemoval);

        this.bindEventListeners();
    }

    bindEventListeners() {
        this.node.addEventListener('click', () => {
            console.log('hello');
        });
    }

    onClassAdd() {
        this.node.classList.add(this.activeClass);
    }

    onClassRemoval() {
        this.node.classList.remove(this.activeClass);
    }
}

export default BackLink;
