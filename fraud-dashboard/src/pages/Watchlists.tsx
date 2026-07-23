import { ListChecks, Plus } from "lucide-react";
import Panel from "@/components/common/Panel";

const mockWatchlists = [
  { id: "w1", entity: "user_5b15258e", type: "User ID", category: "High Risk Velocity", addedBy: "Analyst 402", addedAt: "Today, 01:14 AM" },
  { id: "w2", entity: "fraud_device_001", type: "Device ID", category: "Known Compromised Device", addedBy: "System (Auto)", addedAt: "Yesterday" },
  { id: "w3", entity: "Dubai", type: "Location", category: "Geographic Anomaly Zone", addedBy: "Lead Analyst", addedAt: "3 days ago" },
  { id: "w4", entity: "ACC942109", type: "Receiver Account", category: "Mule Account Suspect", addedBy: "Analyst 108", addedAt: "5 days ago" },
];

export default function Watchlists() {
  return (
    <div className="space-y-lg">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-md">
        <div>
          <div className="flex items-center gap-sm">
            <ListChecks size={28} className="text-primary" />
            <h1 className="font-heading text-headline-md font-bold text-on-surface">
              Entities Watchlist & Blocklists
            </h1>
          </div>
          <p className="font-body text-body-md text-on-surface-variant">
            Active entity monitoring rules and automated blacklists
          </p>
        </div>

        <button className="bg-primary text-on-primary font-label-md px-lg py-sm rounded-lg flex items-center gap-sm hover:opacity-90 transition-all shadow-soft cursor-pointer">
          <Plus size={18} />
          Add Entity to Watchlist
        </button>
      </div>

      <Panel headerBorder bodyClassName="overflow-x-auto">
        <table className="w-full text-left">
          <thead>
            <tr className="bg-surface-container-low">
              <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Target Entity
              </th>
              <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Entity Type
              </th>
              <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Watchlist Category
              </th>
              <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Added By
              </th>
              <th className="px-lg py-md font-label-sm text-label-sm text-on-surface-variant uppercase tracking-wider">
                Added Date
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/10">
            {mockWatchlists.map((w) => (
              <tr key={w.id} className="hover:bg-surface-container-low/50 transition-colors">
                <td className="px-lg py-md font-mono font-bold text-on-surface">
                  {w.entity}
                </td>
                <td className="px-lg py-md font-label-md text-on-surface-variant">
                  <span className="px-2 py-1 bg-surface-container-high rounded text-xs">
                    {w.type}
                  </span>
                </td>
                <td className="px-lg py-md font-label-md text-error">
                  {w.category}
                </td>
                <td className="px-lg py-md font-label-md text-on-surface-variant">
                  {w.addedBy}
                </td>
                <td className="px-lg py-md font-label-md text-on-surface-variant">
                  {w.addedAt}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </Panel>
    </div>
  );
}
