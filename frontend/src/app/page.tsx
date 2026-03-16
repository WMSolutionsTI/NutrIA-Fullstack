
"use client";
import dynamic from 'next/dynamic';

const Hero = dynamic(() => import('../components/Hero'));
const Features = dynamic(() => import('../components/Features'));
const Footer = dynamic(() => import('../components/Footer'));

export default function Home() {
  // Redirecionamento dos botões (ajuste as rotas conforme necessário)
  const handleAdmin = () => {
    window.location.href = '/admin';
  };
  const handleNutri = () => {
    window.location.href = '/nutricionista';
  };

  return (
    <div className="min-h-screen flex flex-col bg-white dark:bg-black">
      <header className="w-full flex justify-between items-center px-8 py-6 bg-white/80 dark:bg-zinc-900/80 shadow-sm sticky top-0 z-20">
        <div className="flex items-center gap-2">
          <img src="/globe.svg" alt="NutrIA Pro Logo" className="w-10 h-10" />
          <span className="text-2xl font-bold bg-gradient-to-r from-green-600 via-blue-600 to-emerald-400 bg-clip-text text-transparent">NutrIA Pro</span>
        </div>
        <div className="flex gap-4">
          <button onClick={handleAdmin} className="rounded-full bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 font-semibold shadow transition-colors">Acesso Admin</button>
          <button onClick={handleNutri} className="rounded-full bg-emerald-500 hover:bg-emerald-600 text-white px-6 py-2 font-semibold shadow transition-colors">Acesso Nutricionista</button>
        </div>
      </header>
      <main className="flex-1 flex flex-col items-center justify-start w-full">
         <Hero />
        <Features />
      </main>
      <Footer />
    </div>
  );
}
