class Sticky {
    static selector() {
        return '.sticky';
    }

    constructor(node) {
        this.node = node;
        this.offset = 80;
        this.apply_sticky_class(node);
        this.bindEvents();
    }

    apply_sticky_class(sticky) {
        const currentOffset = sticky.getBoundingClientRect().top;
        // eslint-disable-next-line radix
        const stickyOffset = parseInt(
            getComputedStyle(sticky).top.replace('px', this.offset),
        );
        const isStuck = currentOffset <= stickyOffset;

        if (
            (CSS.supports && CSS.supports('position', 'sticky')) ||
            CSS.supports('position', '-webkit-sticky')
        ) {
            if (isStuck) {
                sticky.classList.add('js-is-sticky');
            } else {
                sticky.classList.remove('js-is-sticky');
            }
        }
    }

    bindEvents() {
        window.addEventListener(
            'scroll',
            () => {
                this.apply_sticky_class(this.node);
            },
            { passive: true },
        );
    }
}

export default Sticky;
