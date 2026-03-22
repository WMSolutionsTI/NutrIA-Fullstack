import { NextRequest, NextResponse } from "next/server";

const PROTECTED_PATHS = [
  "/nutricionista/painel",
  "/nutricionista/clientes",
  "/nutricionista/agenda",
  "/nutricionista/caixa-de-entrada",
  "/nutricionista/mensagens",
  "/nutricionista/campanhas",
  "/nutricionista/cobrancas",
  "/nutricionista/relatorios",
  "/nutricionista/configuracoes",
  "/nutricionista/onboarding",
  "/nutricionista/primeiro-acesso",
  "/nutricionista/completar-cadastro",
];

export function middleware(request: NextRequest) {
  const token = request.cookies.get("nutria_token")?.value;
  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PATHS.some((p) => pathname.startsWith(p));

  if (isProtected && !token) {
    return NextResponse.redirect(new URL("/nutricionista/login", request.url));
  }
  return NextResponse.next();
}

export const config = {
  matcher: [
    "/nutricionista/:path*",
  ],
};
