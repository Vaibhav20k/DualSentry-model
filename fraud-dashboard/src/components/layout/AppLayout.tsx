import { useState } from "react";
import { Outlet } from "react-router-dom";

import Sidebar from "./Sidebar";
import Navbar from "./Navbar";
import {
  Sheet,
  SheetContent,
  SheetTitle,
} from "@/components/ui/sheet";

export default function AppLayout() {
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <div className="min-h-screen bg-background text-on-surface">
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-50 hidden lg:flex">
        <Sidebar />
      </aside>

      {/* Mobile navigation drawer */}
      <Sheet open={mobileOpen} onOpenChange={setMobileOpen}>
        <SheetContent
          side="left"
          className="w-64 p-0 bg-surface-container-low border-r border-outline-variant/20"
        >
          <SheetTitle className="sr-only">Navigation</SheetTitle>
          <Sidebar onNavigate={() => setMobileOpen(false)} />
        </SheetContent>
      </Sheet>

      <div className="lg:ml-64 flex flex-col min-h-screen">
        <Navbar onMenu={() => setMobileOpen(true)} />
        <main className="flex-1">
          <div className="p-lg max-w-[1600px] mx-auto space-y-lg">
            <Outlet />
          </div>
        </main>
      </div>
    </div>
  );
}
