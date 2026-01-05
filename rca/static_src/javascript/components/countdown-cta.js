import simplyCountdown from 'simplycountdown.js';

class CountdownCTA {
    static selector() {
        return '[data-countdown-cta]';
    }

    constructor(node) {
        this.node = node;
        this.timerElement = this.node.querySelector('[data-countdown-timer]');
        this.countdownDate = this.node.dataset.countdownDate;
        this.initCountdown();
    }

    initCountdown() {
        const date = new Date(this.countdownDate);

        simplyCountdown(this.timerElement, {
            year: date.getFullYear(),
            month: date.getMonth() + 1,
            day: date.getDate(),
            hours: date.getHours(),
            minutes: date.getMinutes(),
            seconds: date.getSeconds(),
            inline: true,
            inlineSeparator: ' : ',
            words: {
                days: { root: 'd', lambda: (root) => root },
                hours: { root: 'h', lambda: (root) => root },
                minutes: { root: 'm', lambda: (root) => root },
                seconds: { root: 's', lambda: (root) => root },
            },
            zeroPad: true,
            refresh: 1000,
        });
    }
}

export default CountdownCTA;
