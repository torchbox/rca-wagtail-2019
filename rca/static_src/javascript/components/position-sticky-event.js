class Sticky {
    static selector() {
        return ".sticky";
    }

    constructor(node) {
        this.node = node;
        this.offset = 80;
        this.apply_sticky_class(node);
        this.bindEvents();
    }

    apply_sticky_class(sticky) {
        var currentOffset = sticky.getBoundingClientRect().top;
        var stickyOffset = parseInt( getComputedStyle(sticky).top.replace('px', this.offset) );
        var isStuck = currentOffset <= stickyOffset;

        if (CSS.supports && CSS.supports('position', 'sticky')) {
            if (isStuck) {
                sticky.classList.add('js-is-sticky');
            } else {
                sticky.classList.remove('js-is-sticky');
            }
        }
    }

    bindEvents() {

        window.addEventListener('scroll', () => {
            this.apply_sticky_class(this.node);
        })

    }
}

export default Sticky;
