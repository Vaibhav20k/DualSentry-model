import {
  LayoutDashboard,
  ShieldAlert,
  ReceiptText,
  ListChecks,
  BarChart3,
  CircleHelp,
  CircleCheck,
  Plus,
  ShieldCheck,
} from "lucide-react";

import SidebarItem from "./SidebarItem";

const navItems = [
  { icon: LayoutDashboard, label: "Dashboard", active: true },
  { icon: ShieldAlert, label: "Risk Queue" },
  { icon: ReceiptText, label: "Transactions" },
  { icon: ListChecks, label: "Watchlists" },
  { icon: BarChart3, label: "Reports" },
];

interface SidebarProps {
  /** Called when a nav item is clicked (used to close the mobile drawer). */
  onNavigate?: () => void;
}

export default function Sidebar({ onNavigate }: SidebarProps) {
  return (
    <nav className="flex flex-col h-full w-64 py-lg px-md gap-lg bg-surface-container-low border-r border-outline-variant/20">
      {/* Brand */}
      <div className="flex items-center gap-sm px-md mb-md">
        <div className="w-8 h-8 bg-primary rounded flex items-center justify-center shrink-0">
          <ShieldCheck className="text-white" size={20} />
        </div>
        <div className="leading-tight">
          <h1 className="font-heading text-headline-sm font-bold text-primary">
            Intelligence
          </h1>
          <p className="font-label-sm text-label-sm text-on-surface-variant opacity-60">
            Fraud Analysis v2.4
          </p>
        </div>
      </div>

      {/* Primary action */}
      <button
        type="button"
        className="mx-md bg-primary text-on-primary font-label-md py-sm rounded-lg flex items-center justify-center gap-sm hover:opacity-90 transition-all shadow-soft"
      >
        <Plus size={18} />
        New Investigation
      </button>

      {/* Primary navigation */}
      <div className="flex flex-col gap-xs mt-md">
        {navItems.map((item) => (
          <SidebarItem
            key={item.label}
            icon={item.icon}
            label={item.label}
            active={item.active}
            onClick={onNavigate}
          />
        ))}
      </div>

      {/* Bottom support cluster */}
      <div className="mt-auto flex flex-col gap-xs border-t border-outline-variant/20 pt-md">
        <SidebarItem
          icon={CircleHelp}
          label="Support"
          onClick={onNavigate}
        />
        <div className="flex items-center gap-md text-on-surface-variant hover:text-on-surface px-md py-sm rounded-lg hover:bg-surface-container-high transition-all">
          <CircleCheck size={20} className="text-secondary shrink-0" />
          <span className="font-label-md text-label-sm">System Status</span>
        </div>
      </div>
    </nav>
  );
}
