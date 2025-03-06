import React, { useState, useEffect, useRef } from 'react';
import { Avatar, AvatarImage, AvatarFallback } from "@/components/ui/avatar";
import { Textarea } from "@/components/ui/textarea";
import { Button } from "@/components/ui/button";
import { Collapsible, CollapsibleTrigger, CollapsibleContent } from "@/components/ui/collapsible";

export default function MainChat() {
    const [inputText, setInputText] = useState('');
    const [messages, setMessages] = useState([]);
    const [showSourceText, setShowSourceText] = useState(false);
    const [promptContext, setPromptContext] = useState([]);
    const websocket = useRef<WebSocket | null>(null);
    const [verboseMode, setVerboseMode] = useState(false);
    const [connectionStatus, setConnectionStatus] = useState('Connecting...');

    // Define the connectWebSocket function to handle WebSocket connections
    const connectWebSocket = () => {
        const protocol = window.location.protocol === 'https:' ? 'wss://' : 'ws://';
        const websocketURL = `/ws`;
        websocket.current = new WebSocket(websocketURL);

        websocket.current.onopen = () => {
            setConnectionStatus('Connected');
            console.log('WebSocket connected');
        };

        websocket.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            handleWebSocketData(data);
        };

        websocket.current.onclose = () => {
            setConnectionStatus('Disconnected');
            console.log('WebSocket closed. Retrying in 5 seconds...');
            setTimeout(connectWebSocket, 5000); // Retry after 5 seconds
        };

        websocket.current.onerror = (error) => {
            setConnectionStatus('Error');
            console.error('WebSocket error:', error);
            console.error('Error Details:', error.message);
        };
    };

    // Call the connectWebSocket function inside useEffect
    useEffect(() => {
        connectWebSocket();

        // Cleanup function to close the WebSocket when the component unmounts
        return () => {
            if (websocket.current) {
                websocket.current.close();
            }
        };
    }, []);

    const handleWebSocketData = (data: any) => {
        switch (data.type) {
            case 'content_block_delta':
                if (data.delta.type === 'text_delta') {
                    setMessages(prevMessages => {
                        const newMessages = [...prevMessages];
                        const lastMessageIndex = newMessages.length - 1;
                        const lastMessage = { ...newMessages[lastMessageIndex] };
                        lastMessage.text += data.delta.text;
                        newMessages[lastMessageIndex] = lastMessage;
                        return newMessages;
                    });
                }
                break;
            case 'content_block_start':
                setMessages(prevMessages => [...prevMessages, { text: '', from: 'AI' }]);
                break;
            case 'error_message':
                setMessages(prevMessages => [...prevMessages, { text: data.text, from: 'AI' }]);
                break;
            case 'filter_info':
                setMessages(prevMessages => [...prevMessages, { text: data.text, from: 'AI' }]);
                break;
            case 'verbose_info':
                setMessages(prevMessages => [...prevMessages, { text: data.text, from: 'Verbose', verbose: true }]);
                break;
            case 'content_block_stop':
                break;
            case 'message_stop':
                console.log('Message stop received:', data);
                const metrics = data['amazon-bedrock-invocationMetrics'];
                const formattedMetrics = Object.entries(metrics)
                    .map(([key, value]) => `${key}: ${value}`)
                    .join('\n');
                setMessages(prevMessages => [...prevMessages, {
                    text: formattedMetrics,
                    from: 'Verbose',
                    verbose: true
                }]);
                break;
            case 'full_response':
                setMessages(prevMessages => [...prevMessages, { text: data.text, from: 'AI' }]);
                break;
            case 'source_text':
                console.log('Source text received:', data.text);
                const cleanedText = data.text.map((item: string) => item.replace(/\n+/g, '\n').trim()); // Replace excessive newlines and trim
                setPromptContext(cleanedText);
                setShowSourceText(false);
                break;
            default:
                console.log('Unhandled data type:', data);
        }
    };

    const handleSendClick = () => {
        if (inputText.trim()) {
            // Check if the WebSocket is open before sending
            if (websocket.current && websocket.current.readyState === WebSocket.OPEN) {
                console.log('Sending message:', inputText); // Log the data being sent
                websocket.current.send(JSON.stringify({ message: inputText }));
                setMessages((prevMessages) => [...prevMessages, { text: inputText, from: 'You' }]);
                setInputText('');
            } else {
                console.error('WebSocket is not open. Current state:', websocket.current?.readyState);
                // Optionally handle the case where the WebSocket is not open, like showing a message to the user
            }
        }
    };

    return (
        <div className="flex-1 justify-center items-center h-screen chat-app-container">
            <div className="flex flex-col w-full max-w-[100%] min-w-[400px] min-h-[500px] bg-background rounded-lg shadow-lg">
                <div className="bg-primary text-primary-foreground px-4 py-3 rounded-t-lg">
                    <h2 className="text-lg font-medium">Elastic Restaurant Reviews 🤖</h2>
                    {/* Display the connection status to the user */}
                    <p className="text-sm">{`Connection Status: ${connectionStatus}`}</p>
                </div>

                <div className="flex-1 overflow-auto p-4 space-y-4">
                    {messages.filter(message => message.from !== 'Verbose' || verboseMode).map((message, index) => (
                        <div key={index}
                             className={`flex items-start gap-3 ${message.from === 'AI' ? 'justify-start' : message.from === 'Verbose' ? 'justify-start' : 'justify-end'}`}>
                            <p className={`text-sm rounded-lg p-3 max-w-[95%] ${message.from === 'AI' ? 'ai-message' : message.from === 'Verbose' ? 'verbose-message' : 'user-message'}`}
                               style={{ whiteSpace: 'pre-wrap' }}>
                                {message.text}
                            </p>
                        </div>
                    ))}
                </div>

                <div className="border-t p-4">
                    <div className="relative">
                        <textarea
                            placeholder="Type your message..."
                            className="textarea-chat"
                            rows={1}
                            value={inputText}
                            onChange={(e) => setInputText(e.target.value)}
                        />
                        <button type="submit" onClick={handleSendClick}
                            className="send-button">
                            <SendIcon className="send-icon w-5 h-5" />
                        </button>
                    </div>
                </div>

                <Collapsible open={showSourceText} onOpenChange={setShowSourceText}>
                    <CollapsibleTrigger asChild>
                        <button className="w-full text-left">
                            Source Text <ChevronsUpDownIcon
                            className={`w-4 h-4 ${showSourceText ? 'transform rotate-180' : ''}`} />
                        </button>
                    </CollapsibleTrigger>
                    <CollapsibleContent className="mt-2 rounded-lg bg-muted overflow-y-auto"
                        style={{ maxHeight: '300px' }}>
                        {Array.isArray(promptContext) ? (
                            promptContext.map((text, index) => (
                                <div key={index} className="mb-4 last:mb-0 rounded-lg shadow source-background">
                                    <p className="text-sm whitespace-pre-wrap p-3">{text}</p>
                                </div>
                            ))
                        ) : (
                            <div className="rounded-lg shadow source-background">
                                <p className="text-sm whitespace-pre-wrap p-3">{promptContext}</p>
                            </div>
                        )}
                    </CollapsibleContent>
                </Collapsible>
            </div>

            <div className="absolute bottom-0 left-0 p-4">
                <label className="flex items-center space-x-2">
                    <input
                        type="checkbox"
                        checked={verboseMode}
                        onChange={(e) => setVerboseMode(e.target.checked)}
                    />
                    <span className="verbose-mode-label">Verbose Mode</span>
                </label>
            </div>
        </div>
    );
}

function ChevronsUpDownIcon(props: any) {
    return (
        <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m7 15 5 5 5-5" />
            <path d="m7 9 5-5 5 5" />
        </svg>
    );
}

function SendIcon(props: any) {
    return (
        <svg {...props} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none"
            stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
            <path d="m22 2-7 20-4-9-9-4Z" />
            <path d="M22 2 11 13" />
        </svg>
    );
}
