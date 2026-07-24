"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";

import { useAuth } from "@/components/AuthProvider";

export function SiteHeader() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  function handleLogout() {
    logout();
    router.push("/");
  }

  return (
    <header className="border-b border-neutral-200 dark:border-neutral-800">
      <nav className="mx-auto flex max-w-5xl items-center justify-between px-6 py-3">
        <Link href="/" className="text-sm font-semibold">
          Great Energy Field
        </Link>
        <div className="flex items-center gap-4 text-sm">
          {loading ? null : user ? (
            <>
              {user.role === "admin" && (
                <Link href="/admin" className="text-neutral-600 hover:underline dark:text-neutral-300">
                  Admin
                </Link>
              )}
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
