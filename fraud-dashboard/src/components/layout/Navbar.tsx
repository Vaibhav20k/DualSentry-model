import { useState } from "react";
import { useNavigate } from "react-router-dom";
import {
  Bell,
  Sun,
  Moon,
  Settings,
  Search,
  Menu,
} from "lucide-react";

import NavbarStatus from "./NavbarStatus";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { useTheme } from "@/context/theme-context";

interface NavbarProps {
  /** Opens the mobile navigation drawer (hidden on desktop). */
  onMenu?: () => void;
  model?: string;
}

export default function Navbar({
  onMenu,
  model = "XGBoost v1.0.4",
}: NavbarProps) {
  const [query, setQuery] = useState("");
  const navigate = useNavigate();
  const { theme, toggleTheme } = useTheme();

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      navigate(`/transactions?search=${encodeURIComponent(query.trim())}`);
    } else {
      navigate(`/transactions`);
    }
  };

  return (
    <header className="flex justify-between items-center w-full px-lg h-16 sticky top-0 z-40 bg-surface-bright border-b border-outline-variant/20 transition-colors">
      <div className="flex items-center gap-xl flex-1 min-w-0">
        <button
          type="button"
          onClick={onMenu}
          aria-label="Open navigation"
          className="lg:hidden p-sm hover:bg-surface-container-low rounded-full transition-colors text-on-surface-variant shrink-0"
        >
          <Menu size={20} />
        </button>

        {/* Search */}
        <form onSubmit={handleSearch} className="flex items-center bg-surface-container-low px-md py-xs rounded-full border border-outline-variant/30 w-full max-w-md">
          <Search
            size={18}
            className="text-on-surface-variant mr-sm shrink-0"
          />
          <input
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search transactions, users, or risks..."
            className="bg-transparent border-none outline-none focus:ring-0 w-full font-body text-body-md text-on-surface placeholder:text-on-surface-variant/70"
          />
        </form>
      </div>

      <div className="flex items-center gap-md shrink-0">
        <NavbarStatus model={model} className="hidden md:flex" />

        <div className="flex gap-sm border-r border-outline-variant/40 pr-md">
          <button
            type="button"
            aria-label="Notifications"
            className="p-sm hover:bg-surface-container-low rounded-full transition-colors text-on-surface-variant relative cursor-pointer"
          >
            <Bell size={20} />
            <span className="absolute top-2 right-2 w-2 h-2 bg-primary rounded-full" />
          </button>
          <button
            type="button"
            onClick={toggleTheme}
            aria-label="Toggle theme"
            className="p-sm hover:bg-surface-container-low rounded-full transition-colors text-on-surface-variant cursor-pointer active:scale-95"
            title={`Switch to ${theme === "light" ? "Dark" : "Light"} mode`}
          >
            {theme === "dark" ? <Sun size={20} className="text-amber-400" /> : <Moon size={20} />}
          </button>
          <button
            type="button"
            aria-label="Settings"
            className="p-sm hover:bg-surface-container-low rounded-full transition-colors text-on-surface-variant"
          >
            <Settings size={20} />
          </button>
        </div>

        <div className="flex items-center gap-sm pl-sm">
          <div className="text-right hidden sm:block">
            <p className="font-label-md text-label-md font-bold text-on-surface">
              Analyst 402
            </p>
            <p className="font-label-sm text-label-sm text-on-surface-variant">
              Level 3 Access
            </p>
          </div>
          <Avatar size="lg" className="border-2 border-primary-fixed">
            <AvatarFallback className="bg-primary-container text-on-primary-container font-label-md">
              A4
            </AvatarFallback>
          </Avatar>
        </div>
      </div>
    </header>
  );
}
