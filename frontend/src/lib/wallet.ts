/** Wallet (Web3) sign-in via an injected EIP-1193 provider (e.g. MetaMask).

 * Uses the standard injected provider directly (no extra deps). A richer
 * multi-wallet UX (RainbowKit/WalletConnect) can layer on later.
 */

import { apiFetch, setToken } from "@/lib/api";
import type { AuthUser } from "@/lib/auth";

interface Eip1193Provider {
  request(args: { method: string; params?: unknown[] }): Promise<unknown>;
}

interface NonceResponse {
  message: string;
  nonce_token: string;
}

interface TokenResponse {
  access_token: string;
  token_type: string;
  user: AuthUser;
}

export class WalletError extends Error {}

function getProvider(): Eip1193Provider {
  const eth = (window as unknown as { ethereum?: Eip1193Provider }).ethereum;
  if (!eth) {
    throw new WalletError("No wallet detected. Please install MetaMask or another Ethereum wallet.");
  }
  return eth;
}

async function connectAndSign(): Promise<{
  address: string;
  signature: string;
  nonce_token: string;
}> {
  const eth = getProvider();
  const accounts = (await eth.request({ method: "eth_requestAccounts" })) as string[];
  const address = accounts?.[0];
  if (!address) throw new WalletError("No wallet account was authorized.");

  const nonce = await apiFetch<NonceResponse>("/api/auth/wallet/nonce", {
    method: "POST",
    body: { address },
  });
  const signature = (await eth.request({
    method: "personal_sign",
    params: [nonce.message, address],
  })) as string;

  return { address, signature, nonce_token: nonce.nonce_token };
}

/** Connect a wallet and sign in (creates a wallet account if new). */
export async function walletLogin(): Promise<AuthUser> {
  const { address, signature, nonce_token } = await connectAndSign();
  const res = await apiFetch<TokenResponse>("/api/auth/wallet/verify", {
    method: "POST",
    body: { address, signature, nonce_token },
  });
  setToken(res.access_token);
  return res.user;
}

/** Link a wallet to the currently signed-in account. */
export async function walletLink(): Promise<void> {
  const { address, signature, nonce_token } = await connectAndSign();
  await apiFetch<unknown>("/api/auth/wallet/link", {
    method: "POST",
    body: { address, signature, nonce_token },
    auth: true,
  });
}
