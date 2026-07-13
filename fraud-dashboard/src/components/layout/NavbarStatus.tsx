import { cn } from "@/lib/utils";

interface NavbarStatusProps {
  model: string;
  status?: string;
  pulse?: boolean;
  className?: string;
}

/** Model-version pill with a live pulse dot (sage). */
export default function NavbarStatus({
  model,
  status = "Active",
  pulse = true,
  className,
}: NavbarStatusProps) {
  return (
    <div
      className={cn(
        "px-md py-xs bg-secondary-container text-on-secondary-fixed-variant rounded-full text-label-sm font-label-sm flex items-center gap-xs",
        className
      )}
    >
      {pulse && (
        <span className="w-1.5 h-1.5 rounded-full bg-secondary animate-pulse" />
      )}
      <span>Model: {model} {status}</span>
    </div>
  );
}
