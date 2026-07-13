import type { LucideIcon } from "lucide-react";

import { cn } from "@/lib/utils";

interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  active?: boolean;
  onClick?: () => void;
}

/**
 * Single navigation row. Active state uses the terracotta primary-container
 * treatment with a subtle scale, matching the Sentinel sidebar spec.
 */
export default function SidebarItem({
  icon: Icon,
  label,
  active = false,
  onClick,
}: SidebarItemProps) {
  return (
    <button
      type="button"
      onClick={onClick}
      aria-current={active ? "page" : undefined}
      className={cn(
        "flex items-center gap-md w-full rounded-lg px-md py-sm",
        active
          ? "bg-primary-container text-on-primary-container scale-[0.98] transition-transform duration-150"
          : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all duration-200"
      )}
    >
      <Icon size={20} className="shrink-0" />
      <span className="font-label-md text-label-md">{label}</span>
    </button>
  );
}
