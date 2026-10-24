import { useEffect, useState } from 'react';
import { apiGet } from '../../lib/apiClient';
const BASE = (import.meta.env.BASE_URL ?? '/').replace(/\/$/, '');

interface Node {
  id: number;
  label: string;
  count: number;
}

interface Edge {
  a: number;
  b: number;
  count: number;
}

// Dependency-free radial layout: nodes on a circle, edge width = count.
// (react-force-graph needs a GitHub-hosted dep unavailable offline.)
export default function DocumentNetwork() {
  const [corpus, setCorpus] = useState('');
  const [nodes, setNodes] = useState<Node[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);

  async function load() {
    if (!corpus) return;
    const g = await apiGet(`/api/contradictions/network?corpus_id=${corpus}`);
    setNodes((g.nodes ?? []) as Node[]);
    setEdges((g.edges ?? []) as Edge[]);
  }

  useEffect(() => {
    const c = new URLSearchParams(window.location.search).get('corpus') ?? '';
    setCorpus(c);
    if (c) {
      apiGet(`/api/contradictions/network?corpus_id=${c}`).then((g) => {
        setNodes((g.nodes ?? []) as Node[]);
        setEdges((g.edges ?? []) as Edge[]);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const W = 760;
  const H = 440;
  const pos = new Map<number, { x: number; y: number }>();
  nodes.forEach((n, i) => {
    const ang = (2 * Math.PI * i) / Math.max(nodes.length, 1) - Math.PI / 2;
    pos.set(n.id, { x: W / 2 + (W / 2 - 70) * Math.cos(ang), y: H / 2 + (H / 2 - 50) * Math.sin(ang) });
  });

  return (
    <div>
      <div className="flex gap-2">
        <input className="border border-slate-300 px-2 py-1" value={corpus} onChange={(e) => setCorpus(e.target.value)} placeholder="Corpus id" />
        <button className="border border-slate-300 px-3 py-1" onClick={load}>Load</button>
      </div>
      {!nodes.length && <p className="mt-2 text-sm opacity-70">Enter a corpus id and load.</p>}
      {nodes.length > 0 && (
        <svg width={W} height={H} className="mt-2 border border-slate-200">
          {edges.map((e, i) => {
            const a = pos.get(e.a);
            const b = pos.get(e.b);
            if (!a || !b) return null;
            return <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="#b45309" strokeWidth={Math.min(1 + e.count, 6)} opacity={0.6} />;
          })}
          {nodes.map((n) => {
            const p = pos.get(n.id)!;
            return (
              <g key={n.id} className="cursor-pointer" onClick={() => { window.location.href = `${BASE}/contradictions?corpus=${corpus}&doc=${n.id}`; }}>
                <circle cx={p.x} cy={p.y} r={10 + Math.min(n.count, 8)} fill="#1e293b" />
                <text x={p.x} y={p.y - 16} textAnchor="middle" fontSize={11} fill="#1e293b">{n.label} ({n.count})</text>
              </g>
            );
          })}
        </svg>
      )}
    </div>
  );
}
