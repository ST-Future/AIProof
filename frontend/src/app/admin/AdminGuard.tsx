"use client";

import { useRouter } from "next/navigation";
import { useEffect, type ReactNode } from "react";

import { useAuth } from "@/components/AuthProvider";

/**
 * Client-side gate for the admin area. Server-side enforcement lives on the
 * FastAPI `require_admin` dependency; this just keeps non-admins out of the UI.
 */
export function AdminGuard({ children }: { children: ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading) {
    return <p className="mx-auto max-w-5xl px-6 py-16 text-sm text-neutral-500">Loading…</p>;
  }
  if (!user) {
    return null; // redirecting to /login
  }
  if (user.role !== "admin") {
    return (
      <div className="mx-auto max-w-5xl px-6 py-16">
        <h1 className="text-xl font-semibold">Not authorized</h1>
        <p className="mt-2 text-sm text-neutral-500">
          This area is for founder/admin accounts only.
        </p>
      </div>
    );
  }
  return <>{children}</>;
}
