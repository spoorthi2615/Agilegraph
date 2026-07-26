export function SectionHead({ title, hint }: { title: string; hint?: string }) {
  return (
    <div className="flex items-start justify-between">
      <div>
        <h3 className="text-sm font-semibold">{title}</h3>
        {hint && <p className="text-xs text-muted-foreground">{hint}</p>}
      </div>
    </div>
  );
}
