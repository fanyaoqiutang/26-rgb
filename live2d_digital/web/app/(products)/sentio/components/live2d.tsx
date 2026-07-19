'use client'

import React, { useEffect } from 'react';
import { LAppDelegate } from '@/lib/live2d/src/lappdelegate';
import { Live2dManager } from '@/lib/live2d/live2dManager';
import * as LAppDefine from '@/lib/live2d/src/lappdefine';
import { Spinner } from '@heroui/react';
import { useSentioBackgroundStore, useSentioCharacterStore } from "@/lib/store/sentio";
import { useTranslations } from 'next-intl';
import { useLive2D } from '../hooks/live2d';

let audioCtx: AudioContext | null = null;
let currentAudioId = 0;

function audioBufferToWav(buffer: AudioBuffer): ArrayBuffer {
    const numCh = buffer.numberOfChannels;
    const sr = buffer.sampleRate;
    const len = buffer.length;
    const bps = 16;
    const blockAlign = numCh * (bps / 8);
    const dataSize = len * blockAlign;
    const ab = new ArrayBuffer(44 + dataSize);
    const v = new DataView(ab);
    const writeStr = (o: number, s: string) => { for (let i = 0; i < s.length; i++) v.setUint8(o + i, s.charCodeAt(i)); };
    writeStr(0, 'RIFF');
    v.setUint32(4, 36 + dataSize, true);
    writeStr(8, 'WAVE');
    writeStr(12, 'fmt ');
    v.setUint32(16, 16, true);
    v.setUint16(20, 1, true);
    v.setUint16(22, numCh, true);
    v.setUint32(24, sr, true);
    v.setUint32(28, sr * blockAlign, true);
    v.setUint16(32, blockAlign, true);
    v.setUint16(34, bps, true);
    writeStr(36, 'data');
    v.setUint32(40, dataSize, true);
    const channels: Float32Array[] = [];
    for (let ch = 0; ch < numCh; ch++) channels.push(buffer.getChannelData(ch));
    let offset = 44;
    for (let i = 0; i < len; i++) {
        for (let ch = 0; ch < numCh; ch++) {
            const s = Math.max(-1, Math.min(1, channels[ch][i]));
            v.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
            offset += 2;
        }
    }
    return ab;
}

export function Live2d() {
    const t = useTranslations('Products.sentio');
    const { ready, setLive2dCharacter } = useLive2D();
    const { background } = useSentioBackgroundStore();
    const { character } = useSentioCharacterStore();

    const handleLoad = () => {
        if (LAppDelegate.getInstance().initialize() == false) return;
        LAppDelegate.getInstance().run();
        if (character) setLive2dCharacter(character);
    };

    const handleResize = () => {
        if (LAppDefine.CanvasSize === 'auto') {
            LAppDelegate.getInstance().onResize();
        }
    };

    const handleBeforeUnload = () => {
        LAppDelegate.releaseInstance();
    };

    useEffect(() => {
        handleLoad();
        window.addEventListener('resize', handleResize);

        const handler = async (event: MessageEvent) => {
            const msg = event.data || {};
            if (msg.type === 'queryPlaying') {
                event.source?.postMessage({ type: 'playingStatus', playing: Live2dManager.getInstance().isAudioPlaying() }, event.origin as any);
                return;
            }
            if (msg.type === 'stopAudio') {
                Live2dManager.getInstance().stopAudio();
                currentAudioId = 0;
                return;
            }
            if (msg.type !== 'playAudio' || !msg.audioUrl) return;
            if (msg.id && msg.id <= currentAudioId) return;
            currentAudioId = msg.id || ++currentAudioId;

            Live2dManager.getInstance().stopAudio();
            if (!audioCtx) audioCtx = new AudioContext();
            if (audioCtx.state === 'suspended') await audioCtx.resume();

            try {
                const resp = await fetch(msg.audioUrl);
                const ab = await resp.arrayBuffer();
                const audioBuffer = await audioCtx.decodeAudioData(ab);
                const wavBuffer = audioBufferToWav(audioBuffer);
                Live2dManager.getInstance().pushAudioQueue(wavBuffer);
            } catch(e) { console.error('[Live2D] audio error:', e); }
        };
        window.addEventListener('message', handler);

        return () => {
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('message', handler);
            handleBeforeUnload();
        };
    }, []);

    return (
        <div className='absolute top-0 left-0 w-full h-full z-0'>
            { background && (background.link.endsWith('.mp4') ?
                <video className='absolute top-0 left-0 w-full h-full object-cover z-[-1]' autoPlay muted loop src={background.link} style={{ pointerEvents: 'none' }} />
                : <img src={background.link} alt="" className='absolute top-0 left-0 w-full h-full object-cover z-[-1]' />
            )}
            { !ready && <div className='absolute top-0 left-0 w-full h-full flex items-center justify-center z-50'>
                <p className='text-xl font-bold'>{t('loading')}</p>
                <Spinner color='warning' variant="dots" size='lg'/>
            </div>}
            <canvas id="live2dCanvas" className='w-full h-full bg-center bg-cover' />
        </div>
    );
}