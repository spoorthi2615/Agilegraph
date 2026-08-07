import { GraphNode, GraphEdge } from "../../lib/types";
import { riskColor } from "../../lib/types";

import React from "react";

export const CryptoGraphCanvas = React.memo(function CryptoGraphCanvas({
  nodes,
  edges,
  zoom,
  setZoom,
  selected,
  onSelect,
}: {
  nodes: GraphNode[];
  edges: GraphEdge[];
  zoom: number;
  setZoom: (z: number | ((z: number) => number)) => void;
  selected: string | null;
  onSelect: (id: string) => void;
}) {
  const [pan, setPan] = React.useState({ x: 0, y: 0 });
  const [isDragging, setIsDragging] = React.useState(false);
  const [lastPos, setLastPos] = React.useState({ x: 0, y: 0 });
  const containerRef = React.useRef<HTMLDivElement>(null);

  React.useEffect(() => {
    const el = containerRef.current;
    if (!el) return;
    const onWheel = (e: WheelEvent) => {
      e.preventDefault();
      const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
      setZoom((z) => Math.min(4, Math.max(0.1, z * zoomFactor)));
    };
    el.addEventListener("wheel", onWheel, { passive: false });
    return () => el.removeEventListener("wheel", onWheel);
  }, [setZoom]);

  const handlePointerDown = (e: React.PointerEvent) => {
    const target = e.target as Element;
    if (target.tagName === "circle" || target.tagName === "text" || target.tagName === "g") {
      return; // Let the node handle its own click
    }
    setIsDragging(true);
    setLastPos({ x: e.clientX, y: e.clientY });
    e.currentTarget.setPointerCapture(e.pointerId);
  };

  const handlePointerMove = (e: React.PointerEvent) => {
    if (!isDragging) return;
    const dx = e.clientX - lastPos.x;
    const dy = e.clientY - lastPos.y;
    setPan((p) => ({ x: p.x + dx, y: p.y + dy }));
    setLastPos({ x: e.clientX, y: e.clientY });
  };

  const handlePointerUp = (e: React.PointerEvent) => {
    setIsDragging(false);
    e.currentTarget.releasePointerCapture(e.pointerId);
  };

  return (
    <div
      ref={containerRef}
      className="grid-bg h-[600px] w-full touch-none cursor-grab active:cursor-grabbing"
      onPointerDown={handlePointerDown}
      onPointerMove={handlePointerMove}
      onPointerUp={handlePointerUp}
      onPointerCancel={handlePointerUp}
    >
      <svg viewBox="0 0 1000 640" className="h-full w-full">
        <g transform={`translate(${pan.x}, ${pan.y}) scale(${zoom})`}>
          {edges.map((e, i) => {
            const s = nodes.find((n) => n.id === e.source);
            const t = nodes.find((n) => n.id === e.target);
            if (!s || !t) return null;
            return (
              <line
                key={i}
                x1={s.x}
                y1={s.y}
                x2={t.x}
                y2={t.y}
                stroke="var(--color-muted-foreground)"
                strokeWidth="1.5"
                opacity="0.4"
              />
            );
          })}
          {nodes.map((n) => {
            const size =
              n.risk === "critical" ? 20 : n.risk === "high" ? 17 : n.risk === "medium" ? 14 : 12;
            const isSel = selected === n.id;
            return (
              <g
                key={n.id}
                className="cursor-pointer outline-none focus-visible:ring-2 focus-visible:ring-primary rounded-full"
                onClick={() => onSelect(n.id)}
                tabIndex={0}
                role="button"
                aria-label={`Select node ${n.label}`}
                onKeyDown={(e) => {
                  if (e.key === "Enter" || e.key === " ") {
                    e.preventDefault();
                    onSelect(n.id);
                  }
                }}
              >
                {isSel && (
                  <circle
                    cx={n.x}
                    cy={n.y}
                    r={size + 8}
                    fill="none"
                    stroke="var(--color-primary)"
                    strokeWidth="2"
                    opacity="0.6"
                  />
                )}
                <circle
                  cx={n.x}
                  cy={n.y}
                  r={size}
                  fill="white"
                  stroke={riskColor[n.risk]}
                  strokeWidth="3"
                />
                <circle cx={n.x} cy={n.y} r={size / 3} fill={riskColor[n.risk]} />
                <text
                  x={n.x}
                  y={n.y + size + 12}
                  textAnchor="middle"
                  fontSize="10"
                  fill="var(--color-muted-foreground)"
                  style={{ pointerEvents: "none" }}
                >
                  {n.label.length > 22 ? n.label.slice(0, 20) + "…" : n.label}
                </text>
              </g>
            );
          })}
        </g>
      </svg>
    </div>
  );
});
