// Re-export types from shared-types for backwards compatibility
export type { UserRole, User, SessionUser, Session } from '@datn/shared-types';

export interface CurrentUser {
  id: string;
  name: string;
  avatar: string;
  email: string;
}
