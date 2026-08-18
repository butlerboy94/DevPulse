// Global auth state, shared across every page/component. Holds the logged-in
// user and their JWT, persisted to the browser's localStorage so a page
// refresh doesn't log anyone out. lib/api.ts reads the token from here to
// stamp it onto every outgoing request.
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";
import type { UserOut } from "@/types/auth";

interface AuthState {
  token: string | null;
  user: UserOut | null;
  setSession: (token: string, user: UserOut) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      token: null,
      user: null,
      // Called after a successful login or registration.
      setSession: (token, user) => set({ token, user }),
      // Called from the navbar's "Log out" button.
      logout: () => set({ token: null, user: null }),
    }),
    {
      name: "devpulse-auth", // localStorage key
      storage: createJSONStorage(() => localStorage),
    }
  )
);
