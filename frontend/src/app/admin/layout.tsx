"use client";

import { usePathname } from "next/navigation";

import AdminSidebar from "@/components/AdminSidebar";

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isLoginPage = pathname === "/admin";

  if (isLoginPage) {
    return <>{children}</>;
  }

  return (
    <div className="min-h-screen bg-[radial-gradient(circle_at_10%_20%,#67e8f922,transparent_35%),radial-gradient(circle_at_90%_0%,#86efac22,transparent_40%),linear-gradient(135deg,#f8fbff_0%,#f2fff8_100%)]">
      <div className="flex min-h-screen">
        <AdminSidebar />
        <div className="flex-1">
          <header className="sticky top-0 z-20 border-b border-zinc-200 bg-white/80 backdrop-blur-xl px-6 py-4">
            <p className="text-sm font-semibold text-zinc-600">
              Administração estratégica • crescimento, operação e retenção
            </p>
          </header>
          <main className="p-5 md:p-8">{children}</main>
        </div>
      </div>
    </div>
  );
}
