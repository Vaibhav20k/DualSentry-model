import { BarChart3, Download } from "lucide-react";
import Panel from "@/components/common/Panel";

export default function Reports() {
  return (
    <div className="space-y-lg">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-md">
        <div>
          <div className="flex items-center gap-sm">
            <BarChart3 size={28} className="text-primary" />
            <h1 className="font-heading text-headline-md font-bold text-on-surface">
              Analytics & Compliance Reports
            </h1>
          </div>
          <p className="font-body text-body-md text-on-surface-variant">
            Export fraud performance metrics, model accuracy metrics, and SAR audit filings
          </p>
        </div>

        <button className="bg-primary text-on-primary font-label-md px-lg py-sm rounded-lg flex items-center gap-sm hover:opacity-90 transition-all shadow-soft cursor-pointer">
          <Download size={18} />
          Export Monthly Summary (PDF)
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-lg">
        <Panel title="Model Performance Report" className="p-md">
          <p className="text-sm text-on-surface-variant mb-md">
            XGBoost v1.0.4 ROC-AUC score: 0.978. Total precision on high-amount anomalies: 94.2%.
          </p>
          <button className="text-primary font-label-md hover:underline">Download CSV</button>
        </Panel>

        <Panel title="SAR Audit Ledger" className="p-md">
          <p className="text-sm text-on-surface-variant mb-md">
            Suspicious Activity Reports filed for regulatory compliance during current billing cycle.
          </p>
          <button className="text-primary font-label-md hover:underline">View Audit Log</button>
        </Panel>

        <Panel title="False Positive Rate" className="p-md">
          <p className="text-sm text-on-surface-variant mb-md">
            Estimated false positive rate across legitimate transactions is currently 0.04%.
          </p>
          <button className="text-primary font-label-md hover:underline">View Metrics</button>
        </Panel>
      </div>
    </div>
  );
}
