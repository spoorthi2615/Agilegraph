import { useState, useRef } from "react";
import { UploadCloud } from "lucide-react";
import { Button } from "./button";
import { toast } from "sonner";

export function Dropzone({
  hint = "Drop your project ZIP file here, or click to browse",
  onFileDrop,
}: {
  hint?: string;
  onFileDrop?: (file: File) => void;
}) {
  const [drag, setDrag] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  return (
    <div
      onDragOver={(e) => {
        e.preventDefault();
        setDrag(true);
      }}
      onDragLeave={() => setDrag(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDrag(false);
        const file = e.dataTransfer.files[0];
        if (file) {
          toast.success("File attached", { description: file.name });
          onFileDrop?.(file);
        }
      }}
      onClick={() => inputRef.current?.click()}
      className={`grid place-items-center rounded-xl border-2 border-dashed p-12 text-center transition-colors cursor-pointer ${drag ? "border-primary bg-primary/5" : "border-border bg-muted/20"}`}
    >
      <input
        type="file"
        className="hidden"
        ref={inputRef}
        onChange={(e) => {
          const file = e.target.files?.[0];
          if (file) {
            toast.success("File attached", { description: file.name });
            onFileDrop?.(file);
          }
        }}
      />
      <div className="grid h-14 w-14 place-items-center rounded-full bg-primary/10 text-primary">
        <UploadCloud className="h-7 w-7" />
      </div>
      <div className="mt-4 text-sm font-medium">{hint}</div>
      <div className="mt-1 text-xs text-muted-foreground">Supports .zip, .tar.gz up to 500 MB</div>
      <Button type="button" variant="outline" size="sm" className="mt-4">
        Choose file
      </Button>
    </div>
  );
}
