"use client";

import Image from "next/image";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { useAuth } from "@/components/AuthProvider";
import { walletLink } from "@/lib/wallet";

export function SiteHeader() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();
  const [walletStatus, setWalletStatus] = useState<string | null>(null);

  function handleLogout() {
    logout();
    router.push("/");
  }

  async function handleLinkWallet() {
    setWalletStatus("Linking…");
    try {
      await walletLink();
      setWalletStatus("Wallet linked");
    } catch (err) {
      setWalletStatus(err instanceof Error ? err.message : "Link failed");
    }
  }

  return (
    <header className="sticky top-0 z-40 border-b border-neutral-200 bg-white/70 backdrop-blur-md dark:border-neutral-800 dark:bg-neutral-950/70">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="flex items-center gap-2">
          <Image
            src="/logo-mark.png"
            alt=""
            width={40}
            height={40}
            unoptimized
            priority
            className="h-9 w-9 object-contain"
          />
          <span className="text-lg font-semibold leading-none tracking-tight text-emerald-600">
            Great Energy Field
          </span>
        </Link>
        <div className="flex items-center gap-4 text-sm">
          {loading ? null : user ? (
            <>
              {user.role === "admin" && (
                <Link href="/admin" className="text-neutral-600 hover:underline dark:text-neutral-300">
                  Admin
                </Link>
              )}
              <Link
                href="/assessment"
                className="text-neutral-600 hover:underline dark:text-neutral-300"
              >
                Assessment
              </Link>
              <button
                onClick={handleLinkWallet}
                title="Link a wallet to this account"
                className="text-neutral-600 hover:underline dark:text-neutral-300"
              >
                {walletStatus ?? "Link wallet"}
              </button>
              <span className="text-neutral-500">{user.display_name || user.role}</span>
              <button
                onClick={handleLogout}
                className="rounded-full border border-neutral-300 px-3 py-1 transition hover:bg-neutral-100 dark:border-neutral-700 dark:hover:bg-neutral-800"
              >
                Sign out
              </button>
            </>
          ) : (
            <Link
              href="/login"
              className="rounded-full bg-emerald-600 px-4 py-1.5 font-medium text-white transition hover:bg-emerald-700"
            >
              Sign in
            </Link>
          )}
        </div>
      </nav>
    </header>
  );
}
