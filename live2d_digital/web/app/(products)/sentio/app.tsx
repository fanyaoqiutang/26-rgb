'use client'

import { useEffect, useState } from "react";
import { Live2d } from './components/live2d';
import ChatBot from './components/chatbot';
import { Header } from './components/header';
import { useAppConfig } from "./hooks/appConfig";
import { Spinner } from "@heroui/react";


export default function App() {
    const { setAppConfig } = useAppConfig();
    const [ isLoading, setIsLoading ] = useState(true);
    const [isEmbed, setIsEmbed] = useState(false);

    useEffect(() => {
        setAppConfig(null);
        const params = new URLSearchParams(window.location.search);
        const embed = params.get('embed') === 'true';
        setIsEmbed(embed);
        setIsLoading(false);

        if (embed) {
            const handler = (event: MessageEvent) => {
                const { type, audioUrl } = event.data || {};
                if (type === 'playAudio' && audioUrl) {
                    const audio = new Audio(audioUrl);
                    audio.crossOrigin = 'anonymous';
                    audio.play().catch(() => {});
                }
            };
            window.addEventListener('message', handler);
        }
    }, [])

    if (isLoading) {
        return <Spinner className="w-screen h-screen z-10" color="secondary" size="lg" variant="wave" />;
    }

    return (
        <div className='w-full h-full'>
            <Live2d />
            {
                !isEmbed &&
                <div className='flex flex-col w-full h-full'>
                    <Header />
                    <ChatBot />
                </div>
            }
        </div>
    );
}