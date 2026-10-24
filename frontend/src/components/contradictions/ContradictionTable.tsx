import { useEffect, useState } from 'react';
import { apiGet } from '../../lib/apiClient';

interface Row {
  id: number;
  doc_a: string;
  doc_b: string;
  severity: string;
  confidence: number;
  summary: string;
}

interface Detail extends Row {
  claim_a: string;
  claim_b: string;
  explanation: string;
  text_a: string;
  text_b: string;
}

const SEVS = ['', 'minor', 'factual', 'fundamental'];

export default function ContradictionTable() {
  const [corpus, setCorpus] = useState('');
  const [severity, setSeverity] = useState('');
  const [doc, setDoc] = useState('');
  const [rows, setRows] = useState<Row[]>([]);
  const [total, setTotal] = useState(0);
  const [open, setOpen] = useState<Record<number, Detail>>({});
  const [error, setError] = useState('');

  async function load() {
    setError('');
    try {
      const q = new URLSearchParams({ corpus_id: corpus, page: '1', page_size: '50' });
      if (severity) q.set('severity', severity);
      if (doc) q.set('doc', doc);
      const data = await apiGet(`/api/contradictions?${q.toString()}`);
      const items = (data.items ?? []) as Row[];
      items.sort((a, b) => b.confidence - a.confidence);
      setRows(items);
      setTotal(data.total as number);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load.');
    }
  }

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setCorpus(params.get('corpus') ?? '');
    setSeverity(params.get('severity') ?? '');
    setDoc(params.get('doc') ?? '');
    if (params.get('corpus')) {
      const q = new URLSearchParams({ corpus_id: params.get('corpus')!, page: '1', page_size: '50' });
      if (params.get('severity')) q.set('severity', params.get('severity')!);
      if (params.get('doc')) q.set('doc', params.get('doc')!);
      apiGet(`/api/contradictions?${q.toString()}`)
        .then((data) => {
          const items = ((data.items ?? []) as Row[]).sort((a, b) => b.confidence - a.confidence);
          setRows(items);
          setTotal(data.total as number);
        })
        .catch((e) => setError(e instanceof Error ? e.message : 'Failed to load.'));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function expand(id: number) {
    if (open[id]) {
      const next = { ...open };
      delete next[id];
      setOpen(next);
      return;
    }
    const data = (await apiGet(`/api/contradictions/${id}`)) as Detail;
    setOpen((o) => ({ ...o, [id]: data }));
  }

  return (
    <div>
      <div className="flex flex-wrap gap-2">
        <input className="border border-slate-300 px-2 py-1" value={corpus} onChange={(e) => setCorpus(e.target.value)} placeholder="Corpus id" />
        <select className="border border-slate-300 px-2 py-1" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          {SEVS.map((s) => (
            <option key={s} value={s}>{s === '' ? 'All severities' : s}</option>
          ))}
        </select>
        <input className="border border-slate-300 px-2 py-1" value={doc} onChange={(e) => setDoc(e.target.value)} placeholder="Doc id filter" />
        <button className="border border-slate-300 px-3 py-1" onClick={load}>Apply</button>
      </div>
      {error && <p className="mt-2 text-sm text-red-700">{error}</p>}
      <p className="mt-2 text-sm opacity-70">{total} contradictions (NLI is imperfect — review each).</p>
      <table className="mt-2 w-full border border-slate-200 text-sm">
        <thead>
          <tr className="bg-slate-50 text-left">
            <th className="px-2 py-1">A vs B</th>
            <th className="px-2 py-1">Severity</th>
            <th className="px-2 py-1">Conf</th>
            <th className="px-2 py-1">Summary</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <>
              <tr key={r.id} className="cursor-pointer border-t border-slate-200 hover:bg-amberbg" onClick={() => expand(r.id)}>
                <td className="px-2 py-1 mono-n">{r.doc_a} vs {r.doc_b}</td>
                <td className="px-2 py-1">{r.severity}</td>
                <td className="px-2 py-1">{r.confidence.toFixed(2)}</td>
                <td className="px-2 py-1">{r.summary}</td>
              </tr>
              {open[r.id] && (
                <tr key={`${r.id}-d`} className="border-t border-slate-200 bg-amberbg">
                  <td colSpan={4} className="px-2 py-2">
                    <div className="grid gap-2 md:grid-cols-2">
                      <p><mark className="bg-amberbg">{open[r.id].claim_a}</mark></p>
                      <p><mark className="bg-amberbg">{open[r.id].claim_b}</mark></p>
                    </div>
                    <p className="mt-2">{open[r.id].explanation}</p>
                  </td>
                </tr>
              )}
            </>
          ))}
        </tbody>
      </table>
    </div>
  );
}
