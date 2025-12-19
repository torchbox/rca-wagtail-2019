/*
    CTA triggers for the following components:
    - Countdown CTA (countdown_cta.html)
    - Collapsible Nav (collapsible_nav.html)
    - CTA modal (cta_modal.html)

    It can be triggered by:
    - Load
    - Inactivity
    - Scroll
    - Exit intent

    The triggers are configured via data attributes on the component.
    - data-cta: The CTA to trigger
    - data-cta-modal: Whether the CTA is a modal
    - data-cta-id: The ID of the CTA
    - data-cta-trigger: The trigger to use ('load', 'inactivity', 'scroll', 'exit')
    - data-cta-delay: The delay in seconds before showing (for inactivity trigger)
    - data-cta-scroll: The scroll threshold percentage before being shown (for scroll trigger)

    CTAs can be dismissed via the close button (if they have data-cta-close). 
    When closed, the CTA will be hidden and the user will not be able to see it again until the next session.
*/

import MicroModal from 'micromodal';

class CTATrigger {
    static selector() {
        return '[data-cta]';
    }

    constructor(node) {
        this.node = node;
        this.id = this.node.dataset.ctaId;
        this.trigger = this.node.dataset.ctaTrigger;
        this.delay = parseInt(this.node.dataset.ctaDelay, 10) || 5;
        this.scrollThreshold = parseInt(this.node.dataset.ctaScroll, 10) || 50;
        // Exit intent sensitivity - distance in pixels from top of viewport
        this.exitIntentSensitivity = 20;
        this.closeButton = this.node.querySelector('[data-cta-close]');
        this.activeClass = 'is-visible';
        this.shown = false;

        // Check if the CTA is a modal (using data attribute)
        this.isModal = this.node.hasAttribute('data-cta-modal');
        // modalId used for MicroModal API
        this.modalId = this.isModal ? this.node.id : null;
        // AbortController for the user triggers (load, inactivity, scroll, exit intent)
        this.abortController = new AbortController();
        // Separate AbortController for close button (needs to persist after CTA is shown)
        this.closeButtonAbortController = new AbortController();
        this.inactivityTimer = null;

        // Check if the CTA has already been dismissed in the current session
        if (this.isDismissed()) {
            return;
        }

        this.bindCloseButtonEvents();
        this.initTrigger();
    }

    // Check if the CTA has already been dismissed in the current session
    isDismissed() {
        if (!this.id) {
            return false;
        }
        const dismissed = sessionStorage.getItem(`cta_dismissed_${this.id}`);
        return dismissed === '1';
    }

    // Check if device supports touch (for exit intent)
    isTouchDevice() {
        return 'ontouchstart' in window || navigator.maxTouchPoints > 0;
    }

    // Initialize the appropriate trigger based on the data attribute
    initTrigger() {
        switch (this.trigger) {
            case 'load':
                this.show();
                break;
            case 'inactivity':
                this.initInactivityTrigger();
                break;
            case 'scroll':
                this.initScrollTrigger();
                break;
            case 'exit':
                this.initExitIntentTrigger();
                break;
            default:
                // No trigger specified, do nothing
                break;
        }
    }

    // Inactivity trigger - show after X seconds of no activity
    initInactivityTrigger() {
        // Events that will reset the inactivity timer
        const activityEvents = [
            'mousemove',
            'keydown',
            'scroll',
            'pointerdown',
            'touchstart',
        ];

        const resetTimer = () => {
            // Prevent the timer from being reset
            // if the CTA has already been shown
            if (this.shown) {
                return;
            }

            // Clear the existing timer if it exists
            if (this.inactivityTimer) {
                clearTimeout(this.inactivityTimer);
            }

            // Show the CTA after the delay
            this.inactivityTimer = setTimeout(() => {
                this.show();
            }, this.delay * 1000);
        };

        // Start the initial timer
        resetTimer();

        // Reset timer on any activity
        activityEvents.forEach((eventType) => {
            document.addEventListener(eventType, resetTimer, {
                signal: this.abortController.signal,
                passive: true,
            });
        });
    }

    // Scroll trigger - show when user scrolls past X% of the page
    initScrollTrigger() {
        const checkScroll = () => {
            // If the CTA has already been shown, return
            if (this.shown) {
                return;
            }

            // Get the scroll position from the top
            const scrollTop = window.scrollY;

            // Get the total scrollable height
            const docHeight = Math.max(
                document.documentElement.scrollHeight - window.innerHeight,
                1, // Prevent division by zero
            );

            // Calculate the scroll percentage
            const scrollPercent = (scrollTop / docHeight) * 100;

            // If the scroll percentage is greater than or equal to the threshold, show the CTA
            if (scrollPercent >= this.scrollThreshold) {
                this.show();
            }
        };

        window.addEventListener('scroll', checkScroll, {
            signal: this.abortController.signal,
            passive: true,
        });

        // Check immediately in case page is already scrolled
        checkScroll();
    }

    // Exit intent trigger - show when mouse leaves viewport at top (desktop only)
    initExitIntentTrigger() {
        // Skip on touch devices
        if (this.isTouchDevice()) {
            return;
        }

        const handleMouseLeave = (e) => {
            // If the CTA has already been shown, return
            if (this.shown) {
                return;
            }

            // Trigger when mouse is at or above the sensitivity threshold from top
            if (e.clientY <= this.exitIntentSensitivity) {
                this.show();
            }
        };

        document.documentElement.addEventListener(
            'mouseleave',
            handleMouseLeave,
            {
                signal: this.abortController.signal,
            },
        );
    }

    // Show the CTA and remove trigger listeners
    show() {
        // If the CTA has already been shown, return
        if (this.shown) {
            return;
        }

        // Set the CTA as shown
        this.shown = true;

        // Use MicroModal API for modals, otherwise use CSS class
        if (this.isModal && this.modalId) {
            // Remove display: none so MicroModal can control visibility
            this.node.style.display = '';

            // Show the modal using MicroModal API
            MicroModal.show(this.modalId);

            // Focus close button after modal is shown
            if (this.closeButton) {
                requestAnimationFrame(() => {
                    this.closeButton.focus();
                });
            }
        } else {
            // Add the CSS class to show the CTA
            this.node.classList.add(this.activeClass);

            // Focus close button if it exists
            if (this.closeButton) {
                this.closeButton.focus();
            }
        }

        this.removeTriggerListeners();
    }

    // Dismiss the CTA and persist to sessionStorage
    dismiss() {
        // For modals, MicroModal handles closing via data-micromodal-close
        // For non-modals, we just need to remove the CSS class
        if (!this.isModal) {
            this.node.classList.remove(this.activeClass);
        }

        // Add the CTA to sessionStorage
        if (this.id) {
            sessionStorage.setItem(`cta_dismissed_${this.id}`, '1');
        }

        // Remove the trigger listeners
        this.removeTriggerListeners();

        // Remove the close button listener
        this.closeButtonAbortController.abort();
    }

    // Remove all trigger event listeners
    removeTriggerListeners() {
        this.abortController.abort();

        // Clear inactivity timer if it exists
        if (this.inactivityTimer) {
            clearTimeout(this.inactivityTimer);
            this.inactivityTimer = null;
        }
    }

    // Add event listener to the close button
    bindCloseButtonEvents() {
        if (!this.closeButton) {
            return;
        }

        this.closeButton.addEventListener(
            'click',
            (e) => {
                // MicroModal handles closing the modal via data-micromodal-close
                // so we need to add to sessionStorage here before MicroModal.close() is called
                if (this.id) {
                    sessionStorage.setItem(`cta_dismissed_${this.id}`, '1');
                }

                // For non-modals we can call dismiss() to add to sessionStorage
                if (!this.isModal) {
                    e.preventDefault();
                    this.dismiss();
                }
            },
            { signal: this.closeButtonAbortController.signal, capture: true },
        );
    }
}

export default CTATrigger;
