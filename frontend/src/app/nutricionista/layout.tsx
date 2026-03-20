"use client";

import React from "react";
import { usePathname } from "next/navigation";

import NutriNavbar from "@/components/NutriNavbar";
import NutriSidebar from "@/components/NutriSidebar";
import { UserProvider } from "@/context/UserContext";

export default function NutriLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const isAuthScreen =
    pathname === "/nutricionista" ||
    pathname === "/nutricionista/login" ||
    pathname === "/nutricionista/cadastro";

  return (
    <UserProvider>
      {isAuthScreen ? (
        <>{children}</>
      ) : (
        <div className="flex min-h-screen bg-gradient-to-br from-emerald-100 via-white to-blue-100 dark:from-zinc-900 dark:via-black dark:to-zinc-800">
          <NutriSidebar />
          <div className="flex-1 flex flex-col">
            <NutriNavbar />
            <main className="flex-1 p-4 md:p-8">{children}</main>
          </div>
        </div>
      )}
    </UserProvider>
  );
}
