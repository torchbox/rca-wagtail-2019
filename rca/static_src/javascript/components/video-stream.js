import videojs from 'video.js';
import 'videojs-contrib-quality-levels';
import 'videojs-hls-quality-selector';

class VideoPlayer {
    static selector() {
        return '[data-hls-video]';
    }

    constructor(node) {
        this.node = node;
        this.initPlayer();
    }

    initPlayer() {
        this.player = videojs(this.node, {
            responsive: true,
            fluid: true,
            controlBar: {
                fullscreenToggle: true,
                volumePanel: { inline: false },
            },
        });

        // Enable HLS quality selector
        this.player.hlsQualitySelector({
            displayCurrentQuality: true,
        });
    }
}

export default VideoPlayer;
