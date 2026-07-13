interface Props {
  label: string;
  value: React.ReactNode;
  className?: string;
}

/** Small uppercase label + prominent metric value (KPI pattern). */
export default function MetricLabel({ label, value, className }: Props) {
  return (
    <div className={className}>
      <p className="font-mono text-label-sm uppercase tracking-wider text-on-surface-variant mb-xs">
        {label}
      </p>
      <p className="font-heading text-headline-md text-on-surface mt-2">{value}</p>
    </div>
  );
}
