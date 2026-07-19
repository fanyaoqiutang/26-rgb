'use client'

import { useEffect, useState } from "react";
import { Live2d } from './components/live2d';
import ChatBot from './components/chatbot';
import { Header } from './components/header';
import { useAppConfig } from "./hooks/appConfig";
import { Spinner } from "@heroui/react";
import { ResourceModel, RESOURCE_TYPE } from "@/lib/protocol";
import { getSrcPath } from "@/lib/path";


export default function App() {
    const { setAppConfig, setCurrentCharacter } = useAppConfig();
    const [ isLoading, setIsLoading ] = useState(true);
    const [isEmbed, setIsEmbed] = useState(false);

    useEffect(() => {
        setAppConfig(null);
        const params = new URLSearchParams(window.location.search);
        const embed = params.get('embed') === 'true';
        setIsEmbed(embed);

        // 从 URL 参数读取角色配置
        const characterParam = params.get('character');
        if (characterParam) {
            const character: ResourceModel = {
                resource_id: `FREE_${characterParam}`,
                name: characterParam,
                type: RESOURCE_TYPE.CHARACTER,
                link: getSrcPath(`sentio/characters/free/${characterParam}/${characterParam}.png`),
            };
            setCurrentCharacter(character);
        }

        setIsLoading(false);
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