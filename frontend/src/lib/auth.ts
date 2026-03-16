export function setAuthToken(token: string) {
  document.cookie = `nutria_token=${token}; path=/;`;
}

export function getAuthToken() {
  const match = document.cookie.match(/nutria_token=([^;]+)/);
  return match ? match[1] : null;
}

export function clearAuthToken() {
  document.cookie = "nutria_token=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT";
}
