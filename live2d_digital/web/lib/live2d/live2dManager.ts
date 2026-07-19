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
      // 播放音频
      const playAudioBuffer = (buffer: AudioBuffer) => {
        console.log('[Live2dManager] playAudioBuffer called, creating source');
        // 停止旧源防止重叠
        if (this._audioSource) {
          try { this._audioSource.onended = null; this._audioSource.stop(); } catch(e) {}
        }
        var source = this._audioContext.createBufferSource();
        source.buffer = buffer;
        source.connect(this._audioContext.destination);
        source.onended = () => {
          this._audioIsPlaying = false;
          this._audioSource = null;
        };
        source.start();
        this._audioSource = source;
      }
      // 创建一个新的 ArrayBuffer 并复制数据, 防止原始数据被decodeAudioData释放
      const newAudioData = audioData.slice(0);
      this._audioContext.decodeAudioData(newAudioData).then(
        buffer => {
          playAudioBuffer(buffer);
        }
      );
      return audioData;
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
    }

    private static _instance: Live2dManager;
    private _ttsQueue: ArrayBuffer[] = [];
    private _audioContext: AudioContext;
    private _audioIsPlaying: boolean;
    private _blocked: boolean;
    private _audioSource: AudioBufferSourceNode | null;
    private _lipFactor: number;
    private _ready: boolean;
  }