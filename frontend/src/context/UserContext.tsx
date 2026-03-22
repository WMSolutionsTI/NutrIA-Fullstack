"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
import { getMe } from "@/lib/api/auth";
import { clearTokens, getAccessToken } from "@/lib/api/client";
import {
  TrialRecord,
  getCurrentTrial,
  getTrialByEmail,
  getTrialDaysLeft,
  isTrialExpired,
  setCurrentTrialEmail,
} from "@/lib/trial";

interface User {
  id: string;
  nome: string;
  email: string;
  role: "nutritionist" | "admin" | "owner" | "secretaria" | "nutri";
}

interface UserContextType {
  user: User | null;
  trial: TrialRecord | null;
  trialDaysLeft: number;
  trialExpired: boolean;
  refreshTrial: (email?: string) => void;
  setUser: (user: User | null) => void;
  logout: () => void;
}

const UserContext = createContext<UserContextType>({
  user: null,
  trial: null,
  trialDaysLeft: 0,
  trialExpired: false,
  refreshTrial: () => {},
  setUser: () => {},
  logout: () => {},
});

export function UserProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [trial, setTrial] = useState<TrialRecord | null>(null);

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      setTrial(getCurrentTrial());
      return;
    }

    getMe()
      .then((profile) => {
        setCurrentTrialEmail(profile.email);
        setUser({
          id: String(profile.id),
          nome: profile.name,
          email: profile.email,
          role: profile.role,
        });
        setTrial(getTrialByEmail(profile.email));
      })
      .catch(() => {
        clearTokens();
        setUser(null);
        setTrial(getCurrentTrial());
      });
  }, []);

  function refreshTrial(email?: string) {
    if (email) {
      setCurrentTrialEmail(email);
      setTrial(getTrialByEmail(email));
      return;
    }
    setTrial(getCurrentTrial());
  }

  function logout() {
    clearTokens();
    setUser(null);
    setTrial(null);
    window.location.href = "/nutricionista/login";
  }

  const trialDaysLeft = trial ? getTrialDaysLeft(trial) : 0;
  const trialExpired = isTrialExpired(trial);

  return (
    <UserContext.Provider
      value={{
        user,
        trial,
        trialDaysLeft,
        trialExpired,
        refreshTrial,
        setUser,
        logout,
      }}
    >
      {children}
    </UserContext.Provider>
  );
}

export function useUser() {
  return useContext(UserContext);
}
