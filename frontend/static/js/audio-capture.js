/**
 * Client-Side Audio Streamer using Web Audio API (Activity 3.2).
 * Streams 16-bit PCM audio chunks over WebSocket to /ws/audio.
 */

class AudioStreamer {
  constructor() {
    this.audioContext = null;
    this.mediaStream = null;
    this.processor = null;
    this.source = null;
    this.ws = null;
    this.isStreaming = false;
  }

  async start(onMetricCallback) {
    if (this.isStreaming) return;

    try {
      this.mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true, video: false });
      
      const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
      this.ws = new WebSocket(`${protocol}//${window.location.host}/ws/audio`);
      this.ws.binaryType = "arraybuffer";

      this.audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      this.source = this.audioContext.createMediaStreamSource(this.mediaStream);
      this.processor = this.audioContext.createScriptProcessor(4096, 1, 1);

      this.processor.onaudioprocess = (e) => {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          const pcmData = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
          }
          this.ws.send(pcmData.buffer);
        }
      };

      this.ws.onmessage = (event) => {
        try {
          const metrics = JSON.parse(event.data);
          if (onMetricCallback) onMetricCallback(metrics);
        } catch (err) {}
      };

      this.source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
      this.isStreaming = true;
      console.log("[AudioStreamer] Microphone audio streaming active.");
    } catch (err) {
      console.warn("[AudioStreamer] Audio capture unavailable or denied. Backend fallback active.", err);
    }
  }

  stop() {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.source) {
      this.source.disconnect();
      this.source = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach(track => track.stop());
      this.mediaStream = null;
    }
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
    this.isStreaming = false;
    console.log("[AudioStreamer] Audio streaming stopped.");
  }
}

window.AudioStreamer = AudioStreamer;
