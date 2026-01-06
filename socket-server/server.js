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

// Typing users storage with server-side timeout tracking
// Format: Map<conversationId, Map<userId, timeoutId>>
const typingUsers = new Map();

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
  const userId = socket.userId;
  
  // Store active connection
  if (!activeConnections.has(userId)) {
    activeConnections.set(userId, new Map());
  }
  activeConnections.get(userId).set(socket.id, {
    id: socket.id,
    userRole: socket.userRole,
    userName: socket.userName,
    joinedConversations: new Set(),
  });

  // ============ Story 7.3: User Room Subscription ============
  // Automatically join user-specific room for global notifications
  const userRoomName = `user:${userId}`;
  socket.join(userRoomName);
  console.log(`User ${userId} joined user room: ${userRoomName}`);

  // Emit online status to relevant parties
  broadcastOnlineStatus(userId, true);

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

      // ============ Story 7.3: conversation-updated Event ============
      // Emit conversation-updated to user rooms for conversation list updates
      await emitConversationUpdated(conversationId, message);

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
    
    // Broadcast to conversation room (exclude sender)
    socket.to(`conversation:${conversationId}`).emit('user-typing', {
      conversation_id: conversationId,
      user_id: socket.userId,
      user_name: socket.userName
    });

    // Server-side timeout tracking
    if (!typingUsers.has(conversationId)) {
      typingUsers.set(conversationId, new Map());
    }

    const conversationTyping = typingUsers.get(conversationId);

    // Clear existing timeout
    if (conversationTyping.has(socket.userId)) {
      clearTimeout(conversationTyping.get(socket.userId));
    }

    // Set 5-second server timeout
    const timeoutId = setTimeout(() => {
      socket.to(`conversation:${conversationId}`).emit('user-stopped-typing', {
        conversation_id: conversationId,
        user_id: socket.userId
      });
      conversationTyping.delete(socket.userId);
    }, 5000);

    conversationTyping.set(socket.userId, timeoutId);
  });

  socket.on('typing-stop', (data) => {
    const { conversationId } = data;
    
    socket.to(`conversation:${conversationId}`).emit('user-stopped-typing', {
      conversation_id: conversationId,
      user_id: socket.userId
    });

    // Clear server timeout
    if (typingUsers.has(conversationId)) {
      const conversationTyping = typingUsers.get(conversationId);
      if (conversationTyping.has(socket.userId)) {
        clearTimeout(conversationTyping.get(socket.userId));
        conversationTyping.delete(socket.userId);
      }
    }
  });

  // ============ Disconnect Handler ============

  socket.on('disconnect', (reason) => {
    // User disconnected - clean up

    // Cleanup typing indicators for all conversations this user was typing in
    typingUsers.forEach((conversationTyping, conversationId) => {
      if (conversationTyping.has(socket.userId)) {
        clearTimeout(conversationTyping.get(socket.userId));
        conversationTyping.delete(socket.userId);

        io.to(`conversation:${conversationId}`).emit('user-stopped-typing', {
          conversation_id: conversationId,
          user_id: socket.userId
        });
      }
    });

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

async function emitConversationUpdated(conversationId, message) {
  try {
    // Get conversation participants from backend API
    const participantsResponse = await axios.get(
      `${process.env.BACKEND_API_URL}/api/v1/messages/conversations/${conversationId}/participants`,
      {
        headers: { Authorization: `Bearer ${process.env.API_SYSTEM_TOKEN || ''}` },
      }
    );

    const { participants } = participantsResponse.data;

    // Emit conversation-updated to each participant's user room
    for (const participantId of participants) {
      try {
        // For simplicity in Story 7.3, calculate unread_count based on whether user is sender
        // In production, you'd want to get actual unread count from database
        const unreadCount = participantId === message.sender_id ? 0 : 1;

        const conversationUpdateData = {
          conversation_id: conversationId,
          last_message: {
            content: message.content,
            timestamp: message.created_at,
            sender_id: message.sender_id,
            sender_name: message.sender_name || 'Unknown' // Include sender name for toast
          },
          unread_count: unreadCount,
          updated_at: new Date().toISOString()
        };

        // Emit to participant's user room
        io.to(`user:${participantId}`).emit('conversation-updated', conversationUpdateData);
        console.log(`Emitted conversation-updated to user:${participantId}`, {
          conversationId,
          unreadCount,
          lastMessage: conversationUpdateData.last_message.content.substring(0, 50)
        });
      } catch (error) {
        console.error(`Error emitting to user ${participantId}:`, error.message);
      }
    }

    console.log(`Emitted conversation-updated for conversation ${conversationId} to ${participants.length} participants`);
  } catch (error) {
    console.error('Error emitting conversation-updated:', error.message);
  }
}

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
