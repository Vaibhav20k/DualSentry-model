import type { LucideIcon } from "lucide-react";
import { Link, useLocation } from "react-router-dom";
import { cn } from "@/lib/utils";

interface SidebarItemProps {
  icon: LucideIcon;
  label: string;
  href?: string;
  active?: boolean;
  onClick?: () => void;
}

export default function SidebarItem({
  icon: Icon,
  label,
  href,
  active,
  onClick,
}: SidebarItemProps) {
  const location = useLocation();
  const isActive = active ?? (href ? location.pathname === href : false);

  const content = (
    <>
      <Icon size={20} className="shrink-0" />
      <span className="font-label-md text-label-md">{label}</span>
    </>
  );

  const className = cn(
    "flex items-center gap-md w-full rounded-lg px-md py-sm cursor-pointer",
    isActive
      ? "bg-primary-container text-on-primary-container scale-[0.98] transition-transform duration-150 font-bold"
      : "text-on-surface-variant hover:text-on-surface hover:bg-surface-container-high transition-all duration-200"
  );

  if (href) {
    return (
      <Link to={href} onClick={onClick} className={className}>
        {content}
      </Link>
    );
  }

  return (
    <button type="button" onClick={onClick} className={className}>
      {content}
    </button>
  );
}
