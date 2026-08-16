// Shared TypeScript types for login/registration, mirroring
// backend/app/schemas/user.py and token.py.

// Body of POST /api/v1/auth/register.
export interface UserCreate {
  email: string;
  username: string;
  password: string;
}

// Response shape of POST /api/v1/auth/register.
export interface UserOut {
  id: number;
  email: string;
  username: string;
  created_at: string;
}

// Response shape of POST /api/v1/auth/login — the JWT to attach to future
// requests as an "Authorization: Bearer <access_token>" header.
export interface Token {
  access_token: string;
  token_type: string;
}
