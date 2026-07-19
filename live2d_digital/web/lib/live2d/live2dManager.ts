import { LAppDelegate } from '@/lib/live2d/src/lappdelegate';
import { ResourceModel } from '@/lib/protocol';

export class Live2dManager {
    // 单例
    public static getInstance(): Live2dManager {
        if (! this._instance) {
            this._instance = new Live2dManager();
        }

        return this._instance;
    }

    public setReady(ready: boolean) {
      this._ready = ready;
    }

    public isReady(): boolean {
      return this._ready;
    }

    public changeCharacter(character: ResourceModel | null) {
      // _subdelegates中只有一个画布, 所以设置第一个即可
      this._ready = false;
      LAppDelegate.getInstance().changeCharacter(character)
    }

    public setLipFactor(weight: number): void {
      this._lipFactor = weight;
    }

    public getLipFactor(): number {
      return this._lipFactor;
    }

    public pushAudioQueue(audioData: ArrayBuffer): void {
      console.log('[Live2dManager] pushAudioQueue called, queue size before:', this._ttsQueue.length);
      this._blocked = false;
      this._ttsQueue.push(audioData);
    }

    public popAudioQueue(): ArrayBuffer | null {
      if (this._ttsQueue.length > 0) {
        const audioData = this._ttsQueue.shift();
        return audioData;
      } else {
        return null;
      }
    }

    public clearAudioQueue(): void {
      this._ttsQueue = [];
    }

    public playAudio(): ArrayBuffer | null {
      if (this._blocked || this._audioIsPlaying) return null;
      const audioData = this.popAudioQueue();
      if (audioData == null) return null;
      console.log('[Live2dManager] playAudio called, queue size now:', this._ttsQueue.length);
      this._audioIsPlaying = true;

      const newAudioData = audioData.slice(0);
      this._audioContext.decodeAudioData(newAudioData).then(
        buffer => {
          // 将解码后的PCM数据转为WAV格式，供LipSync解析
          const wavData = this.audioBufferToWav(buffer);
          // 播放音频
          const playAudioBuffer = (buf: AudioBuffer) => {
            console.log('[Live2dManager] playAudioBuffer called, creating source');
            if (this._audioSource) {
              try { this._audioSource.onended = null; this._audioSource.stop(); } catch(e) {}
            }
            var source = this._audioContext.createBufferSource();
            source.buffer = buf;
            source.connect(this._audioContext.destination);
            source.onended = () => {
              this._audioIsPlaying = false;
              this._audioSource = null;
            };
            source.start();
            this._audioSource = source;
          }
          playAudioBuffer(buffer);
          // 返回WAV格式数据给LipSync
          this._pendingWavData = wavData;
        }
      );
      return this._pendingWavData || audioData;
    }

    private audioBufferToWav(buffer: AudioBuffer): ArrayBuffer {
      const numChannels = buffer.numberOfChannels;
      const sampleRate = buffer.sampleRate;
      const format = 1; // PCM
      const bitDepth = 16;
      const bytesPerSample = bitDepth / 8;
      const blockAlign = numChannels * bytesPerSample;
      const dataLength = buffer.length * blockAlign;
      const headerLength = 44;
      const totalLength = headerLength + dataLength;
      const arrayBuffer = new ArrayBuffer(totalLength);
      const view = new DataView(arrayBuffer);

      const writeString = (offset: number, str: string) => {
        for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i));
      };

      writeString(0, 'RIFF');
      view.setUint32(4, totalLength - 8, true);
      writeString(8, 'WAVE');
      writeString(12, 'fmt ');
      view.setUint32(16, 16, true);
      view.setUint16(20, format, true);
      view.setUint16(22, numChannels, true);
      view.setUint32(24, sampleRate, true);
      view.setUint32(28, sampleRate * blockAlign, true);
      view.setUint16(32, blockAlign, true);
      view.setUint16(34, bitDepth, true);
      writeString(36, 'data');
      view.setUint32(40, dataLength, true);

      const channels: Float32Array[] = [];
      for (let ch = 0; ch < numChannels; ch++) channels.push(buffer.getChannelData(ch));

      let offset = 44;
      for (let i = 0; i < buffer.length; i++) {
        for (let ch = 0; ch < numChannels; ch++) {
          let sample = channels[ch][i];
          sample = Math.max(-1, Math.min(1, sample));
          sample = sample < 0 ? sample * 0x8000 : sample * 0x7FFF;
          view.setInt16(offset, sample, true);
          offset += 2;
        }
      }
      return arrayBuffer;
    }

    public stopAudio(): void {
      this._blocked = false;
      this.clearAudioQueue();
      if (this._audioSource) {
        this._audioSource.onended = null;
        try { this._audioSource.stop(); } catch(e) {}
        this._audioSource = null;
      }
      this._audioIsPlaying = false;
    }

    public isAudioPlaying(): boolean {
      return this._audioIsPlaying;
    }

    constructor() {
      this._audioContext = new (window.AudioContext || (window as any).webkitAudioContext)();
      this._audioIsPlaying = false;
      this._blocked = false;
      this._audioSource = null;
      this._lipFactor = 1.0;
      this._ready = false;
      this._pendingWavData = null;
    }

    private static _instance: Live2dManager;
    private _ttsQueue: ArrayBuffer[] = [];
    private _audioContext: AudioContext;
    private _audioIsPlaying: boolean;
    private _blocked: boolean;
    private _audioSource: AudioBufferSourceNode | null;
    private _lipFactor: number;
    private _ready: boolean;
    private _pendingWavData: ArrayBuffer | null;
  }