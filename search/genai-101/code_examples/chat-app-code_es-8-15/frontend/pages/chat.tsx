// pages/chat.tsx
import React from 'react';
import { MainChat } from '../src/components';

const ChatPage = () => {
  return (
    <div style={{ height: '100vh', display: 'flex', justifyContent: 'center', alignItems: 'center' }}>
      <MainChat />
    </div>
  );
};

export default ChatPage;
