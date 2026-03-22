"use client";

import dynamic from "next/dynamic";
import { useRouter } from "next/navigation";

import { registerTrialLeadFromClick } from "@/lib/trial";

const Hero = dynamic(() => import("../components/Hero"));
const Features = dynamic(() => import("../components/Features"));
const Footer = dynamic(() => import("../components/Footer"));

export default function Home() {
  const router = useRouter();

  function handleAdmin() {
    router.push("/admin");
  }

  function handleNutriLogin() {
    router.push("/nutricionista/login");
  }

  function handleTrialClick() {
    registerTrialLeadFromClick();
    router.push("/nutricionista/cadastro?trial=1");
  }

  return (
    <div className="min-h-screen flex flex-col bg-white">
      <header className="w-full sticky top-0 z-40 border-b border-zinc-200/70 bg-white/85 backdrop-blur-xl">
        <div className="mx-auto max-w-7xl px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <img src="/globe.svg" alt="NutrIA Pro logo" className="w-10 h-10" />
            <div>
              <p className="text-xl font-black text-zinc-900">NutrIA Pro</p>
              <p className="text-xs text-zinc-500">SaaS premium para nutrição</p>
            </div>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleAdmin}
              className="rounded-xl border border-zinc-300 bg-white px-4 py-2 text-sm font-semibold text-zinc-800 hover:bg-zinc-50 transition-colors"
            >
              Acesso Admin
            </button>
            <button
              onClick={handleTrialClick}
              className="rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white px-4 py-2 text-sm font-semibold shadow-[0_10px_24px_rgba(5,150,105,0.30)] transition-all hover:-translate-y-0.5"
            >
              Testar 14 dias grátis
            </button>
          </div>
        </div>
      </header>

      <main className="flex-1">
        <Hero onTrialClick={handleTrialClick} onNutriLoginClick={handleNutriLogin} />
        <Features />
      </main>

      <Footer />
    </div>
  );
}
