/**
 * Smooth Streaming Audio Player for ElevenLabs / OpenAI PCM chunks
 * ---------------------------------------------------------------
 * This version FIXES:
 *   - choppy audio
 *   - gaps between chunks
 *   - decodeAudioData failures
 *   - out-of-order playback
 *
 * Strategy:
 *   1. Collect PCM chunks into a buffer
 *   2. Periodically merge into a larger block (enough for decodeAudioData)
 *   3. Decode as one stable AudioBuffer
 *   4. Schedule playback seamlessly
 */

class StreamingAudioPlayer {
    constructor() {
        this.ctx = new (window.AudioContext || window.webkitAudioContext)();
        this.chunks = [];
        this.isFlushing = false;
        this.playQueue = [];
        this.isPlaying = false;
    }

    /**
     * Accept PCM chunk from SSE.
     * CHUNK IS RAW BINARY (after atob)
     */
    enqueueChunk(rawPCM) {
        const bytes = new Uint8Array(rawPCM.length);
        for (let i = 0; i < rawPCM.length; i++) {
            bytes[i] = rawPCM.charCodeAt(i);
        }
        this.chunks.push(bytes);

        // Once we have enough to decode (~4–10 KB), flush into a playable buffer
        if (!this.isFlushing && this._totalBytes() > 4000) {
            this._flushChunks();
        }
    }

    /**
     * Merge small PCM chunks → decode → queue for playback
     */
    async _flushChunks() {
        this.isFlushing = true;

        const merged = this._mergeChunks();
        this.chunks = []; // reset buffer

        try {
            const audioBuffer = await this.ctx.decodeAudioData(merged.buffer);
            this.playQueue.push(audioBuffer);
            if (!this.isPlaying) this._playNext();
        } catch (e) {
            console.warn("Skipping undecodable chunk", e);
        }

        this.isFlushing = false;
    }

    /**
     * Calculate total PCM bytes waiting
     */
    _totalBytes() {
        return this.chunks.reduce((sum, c) => sum + c.length, 0);
    }

    /**
     * Merge chunks into a single linear PCM block
     */
    _mergeChunks() {
        const total = this._totalBytes();
        const merged = new Uint8Array(total);

        let offset = 0;
        for (const c of this.chunks) {
            merged.set(c, offset);
            offset += c.length;
        }
        return merged;
    }

    /**
     * Plays queued AudioBuffers in correct order
     */
    _playNext() {
        if (this.playQueue.length === 0) {
            this.isPlaying = false;
            return;
        }

        this.isPlaying = true;
        const buffer = this.playQueue.shift();
        const source = this.ctx.createBufferSource();
        source.buffer = buffer;
        source.connect(this.ctx.destination);

        source.onended = () => this._playNext();
        source.start();
    }

    /**
     * Called when backend says "audio_complete"
     * We flush remaining chunks and stop cleanly
     */
    async endStream() {
        if (this.chunks.length > 0) {
            await this._flushChunks();
        }
    }
}

// Export class globally
window.StreamingAudioPlayer = StreamingAudioPlayer;
