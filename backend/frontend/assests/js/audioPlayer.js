/**
 * Ultra-Low-Latency Audio Streaming Player
 * Designed for: ElevenLabs + SSE chunk playback
 * No buffering delays, plays chunk-by-chunk in real time
 */

class StreamingAudioPlayer {
    constructor() {
        this.context = null;
        this.queue = [];
        this.isPlaying = false;
    }

    async init() {
        if (!this.context) {
            this.context = new (window.AudioContext || window.webkitAudioContext)();
            await this.context.resume();
        }
    }

    /**
     * Push raw MPEG chunks (latin1-decoded) to play queue
     */
    async enqueueChunk(latin1Chunk) {
        await this.init();
        const raw = this._latin1ToUint8(latin1Chunk);

        try {
            const audioBuf = await this.context.decodeAudioData(raw.buffer);
            this.queue.push(audioBuf);
            this._playIfIdle();
        } catch (err) {
            console.warn("Decode error (skipped small chunk):", err);
        }
    }

    _latin1ToUint8(str) {
        const arr = new Uint8Array(str.length);
        for (let i = 0; i < str.length; i++) arr[i] = str.charCodeAt(i);
        return arr;
    }

    async _playIfIdle() {
        if (this.isPlaying || this.queue.length === 0) return;

        this.isPlaying = true;

        const buf = this.queue.shift();
        const src = this.context.createBufferSource();
        src.buffer = buf;
        src.connect(this.context.destination);

        src.onended = () => {
            this.isPlaying = false;
            this._playIfIdle();
        };

        src.start(0);
    }

    reset() {
        this.queue = [];
        this.isPlaying = false;
        if (this.context) this.context.close();
        this.context = null;
    }
}

window.StreamingAudioPlayer = StreamingAudioPlayer;
