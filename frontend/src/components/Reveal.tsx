"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";

/**
 * Fades + rises its children into view once, when scrolled near the viewport.
 * Uses IntersectionObserver and only sets state from the (async) callback, so
 * there is no synchronous setState-in-effect. Motion is disabled for users who
 * prefer reduced motion (via `motion-reduce:` utilities), so content is always
 * readable even before/without the animation.
 */
export function Reveal({
  children,
  delay = 0,
  className = "",
}: {
  children: ReactNode;
  delay?: number;
  className?: string;
}) {
  const ref = useRef<HTMLDivElement>(null);
  const [shown, setShown] = useState(false);

  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setShown(true);
            observer.disconnect();
          }
        }
      },
      { threshold: 0.15, rootMargin: "0px 0px -8% 0px" },
    );
    observer.observe(el);
    return () => observer.disconnect();
  }, []);

  return (
    <div
      ref={ref}
      style={{ transitionDelay: shown ? `${delay}ms` : "0ms" }}
      className={
        "transition-all duration-700 ease-out will-change-transform " +
        "motion-reduce:transition-none motion-reduce:!translate-y-0 motion-reduce:!opacity-100 " +
        (shown ? "translate-y-0 opacity-100" : "translate-y-6 opacity-0") +
        (className ? ` ${className}` : "")
      }
    >
      {children}
    </div>
  );
}
