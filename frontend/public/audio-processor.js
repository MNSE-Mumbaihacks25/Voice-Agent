class AudioProcessor extends AudioWorkletProcessor {
  constructor(options) {
    super();
    this.bufferSize = 4096; // 4KB chunks
    this.buffer = new Int16Array(this.bufferSize);
    this.bufferIndex = 0;
    
    // Get sample rate from options or default to 48000
    this.sourceSampleRate = options.processorOptions.sampleRate || 48000;
    this.targetSampleRate = 16000;
    this.ratio = this.sourceSampleRate / this.targetSampleRate;
    this.accumulatedSamples = 0;
  }

  process(inputs, outputs, parameters) {
    const input = inputs[0];
    if (!input || !input.length) return true;

    const channelData = input[0]; // Mono
    
    // Simple downsampling
    for (let i = 0; i < channelData.length; i++) {
      this.accumulatedSamples += 1;
      
      if (this.accumulatedSamples >= this.ratio) {
        this.accumulatedSamples -= this.ratio;
        
        // Convert Float32 (-1.0 to 1.0) to Int16 (-32768 to 32767)
        let s = Math.max(-1, Math.min(1, channelData[i]));
        s = s < 0 ? s * 0x8000 : s * 0x7FFF;
        
        this.buffer[this.bufferIndex++] = s;

        if (this.bufferIndex >= this.bufferSize) {
          this.port.postMessage(this.buffer.slice());
          this.bufferIndex = 0;
        }
      }
    }

    return true;
  }
}

registerProcessor('audio-processor', AudioProcessor);
