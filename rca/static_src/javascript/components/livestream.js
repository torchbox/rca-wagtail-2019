import Hls from 'hls.js';

class HLSPlayer {
    static selector() {
        return '[data-hls-video]';
    }

    constructor(node) {
        this.node = node;
        this.videoSrc = node.getAttribute('data-src');
        this.initPlayer();
    }

    initPlayer() {
        const hls = new Hls();
        hls.loadSource(this.videoSrc);
        hls.attachMedia(this.node);
    }
}

export default HLSPlayer;
