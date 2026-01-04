/**
 * Application configuration with environment variable validation
 */

// Environment variable configuration with fallbacks
export const config = {
  // Socket.io server configuration
  socketUrl: getEnvVar('NEXT_PUBLIC_SOCKET_URL', 'http://localhost:3001'),
  
  // API configuration  
  apiUrl: getEnvVar('NEXT_PUBLIC_API_URL', 'http://localhost:8000'),
  
  // WebSocket configuration
  websocket: {
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 10000,
  },
  
  // Development flags
  isDevelopment: process.env.NODE_ENV === 'development',
  isProduction: process.env.NODE_ENV === 'production',
} as const;

/**
 * Get environment variable with validation and fallback
 */
function getEnvVar(key: string, fallback: string): string {
  const value = process.env[key];
  
  if (!value) {
    if (process.env.NODE_ENV === 'production') {
      console.warn(`Environment variable ${key} not set, using fallback: ${fallback}`);
    }
    return fallback;
  }
  
  // Validate URL format for URL-type environment variables
  if (key.includes('URL')) {
    try {
      new URL(value);
    } catch (error) {
      console.error(`Invalid URL in environment variable ${key}: ${value}`);
      return fallback;
    }
  }
  
  return value;
}

/**
 * Get Socket.io URL with protocol upgrade for production
 */
export function getSocketUrl(): string {
  let url = config.socketUrl;
  
  // In production, upgrade HTTP to HTTPS and WS to WSS automatically
  if (config.isProduction) {
    if (url.startsWith('http://')) {
      url = url.replace('http://', 'https://');
    }
    if (url.startsWith('ws://')) {
      url = url.replace('ws://', 'wss://');
    }
  }
  
  return url;
}

/**
 * Validate all required environment variables
 */
export function validateEnvironment(): { isValid: boolean; errors: string[] } {
  const errors: string[] = [];
  
  // Check required environment variables
  const requiredVars = [
    'NEXT_PUBLIC_SOCKET_URL',
    'NEXT_PUBLIC_API_URL',
  ];
  
  for (const varName of requiredVars) {
    const value = process.env[varName];
    if (!value && config.isProduction) {
      errors.push(`Missing required environment variable: ${varName}`);
    }
  }
  
  return {
    isValid: errors.length === 0,
    errors,
  };
}

export default config;