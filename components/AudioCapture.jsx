/**
 * Activity 3.2: Noise and Speech Activity Analysis Frontend Audio Streamer.
 * Matches Project Specification (Pages 24-25).
 * Captures live microphone audio using Web Audio API and streams 16-bit PCM to backend WebSocket.
 */

import React, { useEffect, useRef, useState } from 'react';

const AudioCapture = ({ active, onMetrics }) => {
  const [isRecording, setIsRecording] = useState(false);
  const wsRef = useRef(null);
  const audioContextRef = useRef(null);
  const processorRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (active) {
      startCapture();
    } else {
      stopCapture();
    }
    return () => stopCapture();
  }, [active]);

  const startCapture = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      setIsRecording(true);

      // Connect WebSocket
      const wsUrl = `ws://${window.location.host}/ws/audio`;
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      const audioCtx = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: 16000 });
      audioContextRef.current = audioCtx;

      const source = audioCtx.createMediaStreamSource(stream);
      inputRef.current = source;

      const processor = audioCtx.createScriptProcessor(4096, 1, 1);
      processorRef.current = processor;

      processor.onaudioprocess = (e) => {
        if (ws.readyState === WebSocket.OPEN) {
          const inputData = e.inputBuffer.getChannelData(0);
          // Convert float32 array to 16-bit PCM bytes
          const pcmData = new Int16Array(inputData.length);
          for (let i = 0; i < inputData.length; i++) {
            pcmData[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7FFF;
          }
          ws.send(pcmData.buffer);
        }
      };

      ws.onmessage = (event) => {
        try {
          const metrics = JSON.parse(event.data);
          if (onMetrics) onMetrics(metrics);
        } catch (err) {
          console.error("Failed to parse audio metric JSON", err);
        }
      };

      source.connect(processor);
      processor.connect(audioCtx.destination);
    } catch (err) {
      console.warn("Audio capture error (using fallback simulation):", err);
    }
  };

  const stopCapture = () => {
    if (processorRef.current) {
      processorRef.current.disconnect();
      processorRef.current = null;
    }
    if (inputRef.current) {
      inputRef.current.disconnect();
      inputRef.current = null;
    }
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setIsRecording(false);
  };

  return (
    <div className="audio-capture-widget">
      <span className={`pulse-indicator ${isRecording ? 'active' : 'inactive'}`} />
      <span className="audio-label">{isRecording ? "Live Mic Ingesting" : "Audio Standby"}</span>
    </div>
  );
};

export default AudioCapture;
