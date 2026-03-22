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
    pathname === "/nutricionista/cadastro" ||
    pathname === "/nutricionista/primeiro-acesso" ||
    pathname === "/nutricionista/completar-cadastro";

  return (
    <UserProvider>
      {isAuthScreen ? (
        <>{children}</>
      ) : (
        <div className="min-h-screen bg-[radial-gradient(circle_at_0%_0%,#a7f3d044,transparent_45%),radial-gradient(circle_at_100%_0%,#67e8f922,transparent_35%),linear-gradient(140deg,#f4fff6_0%,#f7fbff_55%,#f2fff9_100%)]">
          <div className="flex min-h-screen">
          <NutriSidebar />
          <div className="flex-1 flex flex-col">
            <NutriNavbar />
            <main className="flex-1 p-4 md:p-6 xl:p-8">{children}</main>
          </div>
          </div>
        </div>
      )}
    </UserProvider>
  );
}
