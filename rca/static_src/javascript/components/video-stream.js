import videojs from 'video.js';
import { registerIVSTech } from 'amazon-ivs-player';

class VideoPlayer {
    static selector() {
        return '[data-ivs-video]';
    }

    constructor(node) {
        this.node = node;
        this.src = node.dataset.ivsSrc;

        // registerIVSTech is a no-op if the tech has already been registered.
        registerIVSTech(videojs, {
            wasmWorker: node.dataset.ivsWasmWorker,
            wasmBinary: node.dataset.ivsWasmBinary,
        });

        this.initPlayer();
    }

    initPlayer() {
        this.player = videojs(this.node, {
            techOrder: ['AmazonIVS'],
            responsive: true,
            fluid: true,
            controlBar: {
                fullscreenToggle: true,
                volumePanel: { inline: false },
            },
        });

        this.player.ready(() => {
            this.player.src(this.src);
        });
    }
}

export default VideoPlayer;
