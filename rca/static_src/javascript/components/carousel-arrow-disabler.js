// Modify these according to your controls
const classes = {
    controls: 'controls',
    backArrow: 'carousel__button--prev',
    nextArrow: 'carousel__button--next',
};

function ArrowDisabler(Glide, Components) {
    return {
        mount() {
            // Only in effect when rewinding is disabled
            if (Glide.settings.rewind) {
                return;
            }

            Glide.on(['mount.after', 'run'], () => {
                // Filter out arrows_control
                for (let controlItem of Components.Controls.items) {
                    if (
                        controlItem.getAttribute('data-glide-el') !==
                        classes.controls
                    ) {
                        continue;
                    }

                    // Set left arrow state
                    var left = controlItem.querySelector(
                        '.' + classes.backArrow,
                    );
                    if (left) {
                        if (Glide.index === 0) {
                            left.setAttribute('disabled', ''); // Disable on first slide
                        } else {
                            left.removeAttribute('disabled'); // Enable on other slides
                        }
                    }

                    // Set right arrow state
                    var right = controlItem.querySelector(
                        '.' + classes.nextArrow,
                    );
                    if (right) {
                        // Glide.index is based on the active slide
                        // For bound: true, there will be no empty space & the last slide will never become active
                        // Hence add perView to correctly calculate the last slide
                        const lastSlideIndex = Glide.settings.bound
                            ? Glide.index + (Glide.settings.perView - 1)
                            : Glide.index;

                        if (lastSlideIndex === Components.Sizes.length - 1) {
                            right.setAttribute('disabled', ''); // Disable on last slide
                        } else {
                            right.removeAttribute('disabled'); // Disable on other slides
                        }
                    }
                }
            });
        },
    };
}

export default ArrowDisabler;
