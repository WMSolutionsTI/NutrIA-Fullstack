import React from 'react';

export default function Footer() {
  return (
    <footer className="w-full py-8 flex flex-col items-center bg-gradient-to-t from-emerald-50 via-white to-transparent dark:from-zinc-900 dark:via-black dark:to-transparent">
      <div className="text-zinc-500 dark:text-zinc-400 text-sm">
        © {new Date().getFullYear()} NutrIA Pro — Todos os direitos reservados.
      </div>
      <div className="flex gap-4 mt-2">
        <a href="#" className="hover:underline text-emerald-700 dark:text-emerald-300">Política de Privacidade</a>
        <a href="#" className="hover:underline text-emerald-700 dark:text-emerald-300">Termos de Uso</a>
      </div>
    </footer>
  );
}
