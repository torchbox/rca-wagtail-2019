/*
    CTA triggers for the following components:
    - Countdown CTA (countdown_cta.html)
    - Collapsible Nav (collapsible_nav.html)
    - CTA modal (cta_modal.html)

    It can be triggered by:
    - Load

    The triggers are configured via data attributes on the component.
    - data-cta: The CTA to trigger
    - data-cta-id: The ID of the CTA
    - data-cta-trigger: The trigger to use (currently only 'load')

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
        this.closeButton = this.node.querySelector('[data-cta-close]');
        this.activeClass = 'is-visible';
        this.shown = false;

        // Check if the CTA is a modal
        this.isModal = this.node.dataset.ctaModal;
        // modalId used for MicroModal API
        this.modalId = this.isModal ? this.node.id : null;
        // AbortController for the user triggers (load)
        this.abortController = new AbortController();
        // Separate AbortController for close button (needs to persist after CTA is shown)
        this.closeButtonAbortController = new AbortController();

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

    // Initialize the appropriate trigger based on the data attribute
    initTrigger() {
        if (this.trigger === 'load') {
            this.show();
        }
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
