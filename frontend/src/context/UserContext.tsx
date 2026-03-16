"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
import { getAuthToken, clearAuthToken } from "@/lib/auth";

interface User {
  id: string;
  nome: string;
  email: string;
  role: "nutricionista" | "admin";
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
    // TODO: Buscar usuário autenticado via API usando token
    const token = getAuthToken();
    if (token) {
      // Simulação: decodificar token ou buscar user
      setUser({ id: "1", nome: "Nutricionista Exemplo", email: "nutri@email.com", role: "nutricionista" });
    }
  }, []);

  function logout() {
    clearAuthToken();
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
