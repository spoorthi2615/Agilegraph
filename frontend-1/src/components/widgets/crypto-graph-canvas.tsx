import { GraphNode, GraphEdge } from "../../lib/types";
import { riskColor } from "../../lib/types";

import React from "react";

export const CryptoGraphCanvas = React.memo(function CryptoGraphCanvas({ 
  nodes, edges, zoom, selected, onSelect 
}: { 
  nodes: GraphNode[]; edges: GraphEdge[]; zoom: number; selected: string | null; onSelect: (id: string) => void 
}) {
  return (
    <div className="grid-bg h-[600px] w-full">
      <svg viewBox="0 0 1000 640" className="h-full w-full" style={{ transform: `scale(${zoom})`, transformOrigin: "center" }}>
        {edges.map((e, i) => {
          const s = nodes.find((n) => n.id === e.source);
          const t = nodes.find((n) => n.id === e.target);
          if (!s || !t) return null;
          return <line key={i} x1={s.x} y1={s.y} x2={t.x} y2={t.y} stroke="oklch(0.88 0.01 260)" strokeWidth="1" />;
        })}
        {nodes.map((n) => {
          const size = n.risk === "critical" ? 20 : n.risk === "high" ? 17 : n.risk === "medium" ? 14 : 12;
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
              {isSel && <circle cx={n.x} cy={n.y} r={size + 8} fill="none" stroke="var(--color-primary)" strokeWidth="2" opacity="0.6" />}
              <circle cx={n.x} cy={n.y} r={size} fill="white" stroke={riskColor[n.risk]} strokeWidth="3" />
              <circle cx={n.x} cy={n.y} r={size / 3} fill={riskColor[n.risk]} />
              <text x={n.x} y={n.y + size + 12} textAnchor="middle" fontSize="10" fill="var(--color-muted-foreground)" style={{ pointerEvents: "none" }}>
                {n.label.length > 22 ? n.label.slice(0, 20) + "…" : n.label}
              </text>
            </g>
          );
        })}
      </svg>
    </div>
  );
});
