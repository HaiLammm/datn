/**
 * Environment validation utility
 * Call this during app startup to validate required environment variables
 */

import { validateEnvironment, config } from './config';

/**
 * Validates environment configuration and logs warnings/errors
 * Should be called once during app initialization
 */
export function initializeEnvironment(): void {
  const { isValid, errors } = validateEnvironment();
  
  if (!isValid) {
    console.error('Environment validation failed:');
    errors.forEach(error => console.error(`  - ${error}`));
    
    if (config.isProduction) {
      throw new Error('Invalid environment configuration in production');
    }
  }
  
  // Log configuration in development
  if (config.isDevelopment) {
    console.log('Environment Configuration:');
    console.log(`  Socket URL: ${config.socketUrl}`);
    console.log(`  API URL: ${config.apiUrl}`);
    console.log(`  Environment: ${process.env.NODE_ENV}`);
  }
}