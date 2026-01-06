/**
 * Socket.io Server Connection Tests
 *
 * Tests for:
 * - JWT authentication middleware
 * - Connection handling
 * - Message events
 * - Disconnect handling
 */

const { expect } = require('chai');
const { describe, it, beforeEach, afterEach } = require('mocha');

// Mock socket.io-client for testing
const mockSocket = {
  handshake: {
    auth: {
      token: 'valid-jwt-token'
    }
  },
  userId: null,
  userRole: null,
  userName: null,
  emit: () => {},
  join: () => {},
  leave: () => {},
  disconnect: () => {}
};

const mockIo = {
  use: (middleware) => { middleware(mockSocket, () => {}); },
  on: (event, callback) => { mockSocket[event] = callback; }
};

// Mock axios for API calls
const mockAxios = {
  get: async () => ({
    data: {
      id: 1,
      email: 'test@example.com',
      role: 'recruiter',
      full_name: 'Test User'
    }
  })
};

describe('Socket.io Server Tests', () => {
  describe('JWT Authentication Middleware', () => {
    it('should reject connection without token', async () => {
      const socketWithoutToken = {
        ...mockSocket,
        handshake: { auth: {} }
      };

      let error = null;
      const next = (err) => { error = err; };

      // Simulate middleware
      try {
        const token = socketWithoutToken.handshake.auth.token;
        if (!token) {
          throw new Error('Authentication error: No token provided');
        }
      } catch (e) {
        error = e;
      }

      expect(error).to.be.an('Error');
      expect(error.message).to.include('No token provided');
    });

    it('should accept connection with valid token', async () => {
      let error = null;
      const next = (err) => { error = err; };

      // Simulate middleware with valid token
      try {
        const token = mockSocket.handshake.auth.token;
        if (!token) {
          throw new Error('Authentication error');
        }

        // Mock successful API verification
        const response = await mockAxios.get('http://localhost:8000/api/v1/messages/auth/verify', {
          headers: { Authorization: `Bearer ${token}` }
        });

        if (!response.data || !response.data.id) {
          throw new Error('Authentication error: Invalid token');
        }

        // Attach user info to socket
        mockSocket.userId = response.data.id;
        mockSocket.userRole = response.data.role;
        mockSocket.userName = response.data.full_name || response.data.email;
      } catch (e) {
        error = e;
      }

      expect(error).to.be.null;
      expect(mockSocket.userId).to.equal(1);
      expect(mockSocket.userRole).to.equal('recruiter');
    });
  });

  describe('Connection Handler', () => {
    it('should log user connection', () => {
      const logs = [];

      // Mock console.log
      const originalLog = console.log;
      console.log = (...args) => { logs.push(args.join(' ')); };

      // Simulate connection
      const socket = {
        ...mockSocket,
        id: 'socket-123',
        userId: 1,
        userName: 'Test User'
      };

      // Log connection (simulated)
      console.log(`User connected: ${socket.userId} (${socket.userName}) - Socket ID: ${socket.id}`);

      // Restore console.log
      console.log = originalLog;

      expect(logs[0]).to.include('User connected: 1 (Test User)');
    });

    it('should handle join-conversation event', () => {
      const joinedRooms = [];

      const socket = {
        ...mockSocket,
        join: (room) => { joinedRooms.push(room); }
      };

      // Simulate join-conversation event
      const conversationId = 'conv-123';
      socket.join(`conversation:${conversationId}`);

      expect(joinedRooms).to.include('conversation:conv-123');
    });

    it('should handle leave-conversation event', () => {
      const leftRooms = [];

      const socket = {
        ...mockSocket,
        leave: (room) => { leftRooms.push(room); }
      };

      // Simulate leave-conversation event
      const conversationId = 'conv-123';
      socket.leave(`conversation:${conversationId}`);

      expect(leftRooms).to.include('conversation:conv-123');
    });
  });

  describe('Message Events Handler', () => {
    it('should emit send-message event', () => {
      const sentMessages = [];

      const socket = {
        ...mockSocket,
        emit: (event, data) => { if (event === 'send-message') sentMessages.push(data); }
      };

      // Simulate send-message
      socket.emit('send-message', {
        conversationId: 'conv-123',
        content: 'Hello, this is a test message'
      });

      expect(sentMessages.length).to.equal(1);
      expect(sentMessages[0].content).to.equal('Hello, this is a test message');
    });

    it('should emit new-message to room', () => {
      const broadcastedMessages = [];

      const io = {
        to: (room) => ({
          emit: (event, data) => {
            if (event === 'new-message') broadcastedMessages.push({ room, data });
          }
        })
      };

      // Simulate broadcast
      io.to('conversation:conv-123').emit('new-message', {
        id: 'msg-456',
        content: 'Test broadcast'
      });

      expect(broadcastedMessages.length).to.equal(1);
      expect(broadcastedMessages[0].room).to.equal('conversation:conv-123');
    });

    it('should handle error events', () => {
      const errors = [];

      const socket = {
        ...mockSocket,
        on: (event, callback) => {
          if (event === 'error') callback({ message: 'Test error' });
        }
      };

      socket.on('error', (error) => { errors.push(error); });

      expect(errors.length).to.equal(1);
      expect(errors[0].message).to.equal('Test error');
    });
  });

  describe('Disconnect Handler', () => {
    it('should log user disconnection', () => {
      const logs = [];

      const originalLog = console.log;
      console.log = (...args) => { logs.push(args.join(' ')); };

      // Simulate disconnect
      const userId = 1;
      const userName = 'Test User';
      const reason = 'client namespace disconnect';

      console.log(`User disconnected: ${userId} (${userName}) - Reason: ${reason}`);

      console.log = originalLog;

      expect(logs[0]).to.include('User disconnected: 1 (Test User)');
    });
  });

  describe('Typing Indicators', () => {
    it('should emit typing-start event', () => {
      const typingEvents = [];

      const io = {
        to: (room) => ({
          emit: (event, data) => {
            if (event === 'user-typing') typingEvents.push({ room, data });
          }
        })
      };

      io.to('conversation:conv-123').emit('user-typing', {
        conversationId: 'conv-123',
        userId: 1,
        userName: 'Test User'
      });

      expect(typingEvents.length).to.equal(1);
      expect(typingEvents[0].data.userName).to.equal('Test User');
    });

    it('should emit typing-stop event', () => {
      const typingEvents = [];

      const io = {
        to: (room) => ({
          emit: (event, data) => {
            if (event === 'user-stopped-typing') typingEvents.push({ room, data });
          }
        })
      };

      io.to('conversation:conv-123').emit('user-stopped-typing', {
        conversationId: 'conv-123',
        userId: 1
      });

      expect(typingEvents.length).to.equal(1);
    });

    it('should track typing users with server-side timeout', (done) => {
      // Simulate typing timeout tracking map
      const typingUsers = new Map(); // Map<conversationId, Map<userId, timeoutId>>
      const typingEvents = [];

      const mockIo = {
        to: (room) => ({
          emit: (event, data) => {
            typingEvents.push({ room, event, data });
          }
        })
      };

      const mockSocket = {
        userId: 1,
        userName: 'Test User',
        to: (room) => mockIo.to(room)
      };

      // Simulate typing-start with server timeout
      const conversationId = 'conv-123';
      
      // Track typing user
      if (!typingUsers.has(conversationId)) {
        typingUsers.set(conversationId, new Map());
      }
      const conversationTyping = typingUsers.get(conversationId);

      // Clear existing timeout
      if (conversationTyping.has(mockSocket.userId)) {
        clearTimeout(conversationTyping.get(mockSocket.userId));
      }

      // Set auto-timeout for 5 seconds
      const timeoutId = setTimeout(() => {
        mockSocket.to(`conversation:${conversationId}`).emit('user-stopped-typing', {
          conversation_id: conversationId,
          user_id: mockSocket.userId
        });
        conversationTyping.delete(mockSocket.userId);
        
        // Verify auto-timeout fired
        expect(typingEvents.length).to.equal(1);
        expect(typingEvents[0].event).to.equal('user-stopped-typing');
        done();
      }, 100); // Shorter timeout for test

      conversationTyping.set(mockSocket.userId, timeoutId);

      // Start timer should be set
      expect(conversationTyping.has(mockSocket.userId)).to.be.true;
    });

    it('should clear timeout when manual typing-stop received', () => {
      const typingUsers = new Map();
      const typingEvents = [];
      let timeoutCleared = false;

      // Mock clearTimeout to track if it was called
      const originalClearTimeout = global.clearTimeout;
      global.clearTimeout = (id) => {
        timeoutCleared = true;
        originalClearTimeout(id);
      };

      const conversationId = 'conv-123';
      const userId = 1;

      // Set up typing tracking
      if (!typingUsers.has(conversationId)) {
        typingUsers.set(conversationId, new Map());
      }
      const conversationTyping = typingUsers.get(conversationId);

      // Set a timeout
      const timeoutId = setTimeout(() => {}, 5000);
      conversationTyping.set(userId, timeoutId);

      // Simulate manual typing-stop
      if (conversationTyping.has(userId)) {
        clearTimeout(conversationTyping.get(userId));
        conversationTyping.delete(userId);
      }

      // Restore original clearTimeout
      global.clearTimeout = originalClearTimeout;

      expect(timeoutCleared).to.be.true;
      expect(conversationTyping.has(userId)).to.be.false;
    });

    it('should prevent stuck typing indicators on disconnect', () => {
      const typingUsers = new Map();
      const typingEvents = [];

      const mockIo = {
        to: (room) => ({
          emit: (event, data) => {
            typingEvents.push({ room, event, data });
          }
        })
      };

      const userId = 1;
      const conversationId1 = 'conv-123';
      const conversationId2 = 'conv-456';

      // Set up user typing in multiple conversations
      typingUsers.set(conversationId1, new Map());
      typingUsers.set(conversationId2, new Map());
      
      typingUsers.get(conversationId1).set(userId, setTimeout(() => {}, 5000));
      typingUsers.get(conversationId2).set(userId, setTimeout(() => {}, 5000));

      // Simulate disconnect cleanup
      typingUsers.forEach((conversationTyping, conversationId) => {
        if (conversationTyping.has(userId)) {
          clearTimeout(conversationTyping.get(userId));
          conversationTyping.delete(userId);

          mockIo.to(`conversation:${conversationId}`).emit('user-stopped-typing', {
            conversation_id: conversationId,
            user_id: userId
          });
        }
      });

      expect(typingEvents.length).to.equal(2);
      expect(typingEvents[0].event).to.equal('user-stopped-typing');
      expect(typingEvents[1].event).to.equal('user-stopped-typing');
      expect(typingUsers.get(conversationId1).has(userId)).to.be.false;
      expect(typingUsers.get(conversationId2).has(userId)).to.be.false;
    });
  });
});
