const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const cors = require('cors');
const axios = require('axios');
require('dotenv').config();

const app = express();
const httpServer = createServer(app);

// Socket.io configuration with CORS
const io = new Server(httpServer, {
  cors: {
    origin: process.env.FRONTEND_URL || 'http://localhost:3000',
    credentials: true,
  },
  transports: ['websocket', 'polling'],
});

// Active connections storage (in-memory for simple deployment)
// Format: { userId: { socketId: { id, userRole, userName, joinedConversations } } }
const activeConnections = new Map();

// ============ JWT Authentication Middleware ============

io.use(async (socket, next) => {
  try {
    const token = socket.handshake.auth.token;

    if (!token) {
      // No token provided - reject silently 
      return next(new Error('Authentication error: No token provided'));
    }

    // Verify JWT with FastAPI
    const response = await axios.get(
      `${process.env.BACKEND_API_URL}/api/v1/messages/auth/verify`,
      {
        headers: { Authorization: `Bearer ${token}` },
      }
    );

    if (!response.data || !response.data.id) {
      // Invalid token response - reject silently
      return next(new Error('Authentication error: Invalid token'));
    }

    // Attach user info to socket
    socket.userId = response.data.id;
    socket.userRole = response.data.role;
    socket.userName = response.data.full_name || response.data.email;

    // User authenticated successfully
    next();
  } catch (error) {
    console.error('Socket authentication error:', error.message);
    next(new Error('Authentication error: ' + (error.response?.data?.detail || 'Token verification failed')));
  }
});

// ============ Connection Handler ============

io.on('connection', (socket) => {
  // User connected - store in active connections

  // Store active connection
  if (!activeConnections.has(socket.userId)) {
    activeConnections.set(socket.userId, new Map());
  }
  activeConnections.get(socket.userId).set(socket.id, {
    id: socket.id,
    userRole: socket.userRole,
    userName: socket.userName,
    joinedConversations: new Set(),
  });

  // Emit online status to relevant parties
  broadcastOnlineStatus(socket.userId, true);

  // ============ Join Conversation Handler ============

  socket.on('join-conversation', (conversationId) => {
    const roomName = `conversation:${conversationId}`;
    socket.join(roomName);

    // Track which conversations this socket has joined
    const userConnections = activeConnections.get(socket.userId);
    if (userConnections && userConnections.has(socket.id)) {
      userConnections.get(socket.id).joinedConversations.add(conversationId);
    }

    // User joined conversation room

    // Confirm join to the requesting socket
    socket.emit('conversation-joined', {
      conversationId,
      timestamp: new Date().toISOString(),
    });
  });

  // ============ Leave Conversation Handler ============

  socket.on('leave-conversation', (conversationId) => {
    const roomName = `conversation:${conversationId}`;
    socket.leave(roomName);

    // Remove from tracked conversations
    const userConnections = activeConnections.get(socket.userId);
    if (userConnections && userConnections.has(socket.id)) {
      userConnections.get(socket.id).joinedConversations.delete(conversationId);
    }

    // User left conversation room
  });

  // ============ Send Message Handler ============

  socket.on('send-message', async (data) => {
    try {
      const { conversationId, content } = data;

      if (!conversationId || !content) {
        socket.emit('error', { message: 'Invalid message data' });
        return;
      }

      // Save message via FastAPI
      const response = await axios.post(
        `${process.env.BACKEND_API_URL}/api/v1/messages`,
        {
          conversation_id: conversationId,
          content: content,
        },
        {
          headers: { Authorization: `Bearer ${socket.handshake.auth.token}` },
        }
      );

      const message = response.data;

      // Broadcast to all participants in the conversation room
      io.to(`conversation:${conversationId}`).emit('new-message', message);

      // Message sent successfully and broadcasted

      // Send confirmation to sender
      socket.emit('message-sent', {
        messageId: message.id,
        timestamp: message.created_at,
      });
    } catch (error) {
      console.error('Error sending message:', error.message);
      socket.emit('error', {
        message: 'Failed to send message',
        details: error.response?.data?.detail || error.message,
      });
    }
  });

  // ============ Typing Indicator Handler ============

  socket.on('typing-start', (data) => {
    const { conversationId } = data;
    socket.to(`conversation:${conversationId}`).emit('user-typing', {
      conversationId,
      userId: socket.userId,
      userName: socket.userName,
    });
  });

  socket.on('typing-stop', (data) => {
    const { conversationId } = data;
    socket.to(`conversation:${conversationId}`).emit('user-stopped-typing', {
      conversationId,
      userId: socket.userId,
    });
  });

  // ============ Disconnect Handler ============

  socket.on('disconnect', (reason) => {
    // User disconnected - clean up

    // Remove from active connections
    const userConnections = activeConnections.get(socket.userId);
    if (userConnections) {
      userConnections.delete(socket.id);

      // If no more connections for this user, broadcast offline status
      if (userConnections.size === 0) {
        activeConnections.delete(socket.userId);
        broadcastOnlineStatus(socket.userId, false);
      }
    }
  });
});

// ============ Helper Functions ============

function broadcastOnlineStatus(userId, isOnline) {
  // In a real app, this would broadcast to all conversations the user is part of
  // For now, we just log it
  // User online status changed
}

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({
    status: 'ok',
    connections: activeConnections.size,
    timestamp: new Date().toISOString(),
  });
});

// Get online users count
app.get('/online-users', (req, res) => {
  res.json({
    count: activeConnections.size,
    users: Array.from(activeConnections.keys()),
  });
});

// Start server
const PORT = process.env.PORT || 3001;
httpServer.listen(PORT, () => {
  console.log(`Socket.io server running on port ${PORT}`);
  console.log(`Frontend URL: ${process.env.FRONTEND_URL || 'http://localhost:3000'}`);
  console.log(`Backend API URL: ${process.env.BACKEND_API_URL || 'http://localhost:8000'}`);
});

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('Received SIGTERM, shutting down gracefully...');
  io.close(() => {
    console.log('Socket.io server closed');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('Received SIGINT, shutting down gracefully...');
  io.close(() => {
    console.log('Socket.io server closed');
    process.exit(0);
  });
});
