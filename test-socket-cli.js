#!/usr/bin/env node

// Quick Socket.io client test
const { io } = require('socket.io-client');

console.log('🧪 Testing Socket.io connection from command line...');

// Get a test JWT token (replace with real one)
const testToken = 'your-jwt-token-here'; // Cần lấy từ browser

const socket = io('http://localhost:3001', {
  auth: { token: testToken },
  transports: ['websocket', 'polling']
});

socket.on('connect', () => {
  console.log('✅ Connected! Socket ID:', socket.id);
  
  // Join test conversation
  socket.emit('join-conversation', 'test-123');
  
  // Send test message
  setTimeout(() => {
    socket.emit('send-message', {
      conversationId: 'test-123',
      content: 'Hello from CLI test!'
    });
  }, 1000);
});

socket.on('connect_error', (error) => {
  console.error('❌ Connection error:', error.message);
});

socket.on('conversation-joined', (data) => {
  console.log('📍 Joined conversation:', data);
});

socket.on('new-message', (message) => {
  console.log('📨 New message:', message);
});

setTimeout(() => {
  socket.disconnect();
  console.log('🔚 Test completed');
  process.exit(0);
}, 5000);