"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import type { ReactNode } from "react";

import { AdminGuard } from "@/app/admin/AdminGuard";
import { ADMIN_SECTIONS } from "@/components/admin/sections";

const NAV = [{ href: "/admin", label: "Overview" }, ...ADMIN_SECTIONS];

export function AdminShell({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <AdminGuard>
      <div className="mx-auto flex w-full max-w-6xl flex-col gap-8 px-6 py-10 sm:flex-row">
        <aside className="w-full shrink-0 sm:w-52">
          <nav className="flex flex-row gap-1 overflow-x-auto sm:flex-col">
            {NAV.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={
                    "whitespace-nowrap rounded-lg px-3 py-2 text-sm transition " +
                    (active
                      ? "bg-emerald-600 text-white"
                      : "text-neutral-600 hover:bg-neutral-100 dark:text-neutral-300 dark:hover:bg-neutral-800")
                  }
                >
                  {item.label}
                </Link>
              );
            })}
          </nav>
        </aside>
        <div className="min-w-0 flex-1">{children}</div>
      </div>
    </AdminGuard>
  );
}
