"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
import { getMe } from "@/lib/api/auth";
import { clearTokens, getAccessToken } from "@/lib/api/client";

interface User {
  id: string;
  nome: string;
  email: string;
  role: "nutritionist" | "admin" | "owner" | "secretaria" | "nutri";
}

interface UserContextType {
  user: User | null;
  setUser: (user: User | null) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType>({
  user: null,
  setUser: () => {},
  logout: () => {},
});

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) return;

    getMe()
      .then((profile) => {
        setUser({
          id: String(profile.id),
          nome: profile.name,
          email: profile.email,
          role: profile.role,
        });
      })
      .catch(() => {
        clearTokens();
        setUser(null);
      });
  }, []);

  function logout() {
    clearTokens();
    setUser(null);
    window.location.href = "/nutricionista/login";
  }

  return (
    <UserContext.Provider value={{ user, setUser, logout }}>
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
