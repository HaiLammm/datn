import { apiClient } from './api-client';
import type { User, UserStats } from '@datn/shared-types';

/**
 * Get the current user's profile data
 */
async function getCurrentUser(accessToken: string): Promise<User> {
  const response = await apiClient.get('/users/me', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  return response.data;
}

/**
 * Get the current user's statistics
 */
async function getUserStats(accessToken: string): Promise<UserStats> {
  const response = await apiClient.get('/users/me/stats', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
  return response.data;
}

/**
 * Delete the current user's account and all associated data
 */
async function deleteAccount(accessToken: string): Promise<void> {
  await apiClient.delete('/users/me', {
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  });
}

export const userService = {
  getCurrentUser,
  getUserStats,
  deleteAccount,
};
