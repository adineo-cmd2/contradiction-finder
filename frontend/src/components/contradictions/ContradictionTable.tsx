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
      <div className="filter-bar">
        <input className="input" value={corpus} onChange={(e) => setCorpus(e.target.value)} placeholder="Corpus id" />
        <select className="select" value={severity} onChange={(e) => setSeverity(e.target.value)}>
          {SEVS.map((s) => (
            <option key={s} value={s}>{s === '' ? 'All severities' : s}</option>
          ))}
        </select>
        <input className="input" value={doc} onChange={(e) => setDoc(e.target.value)} placeholder="Doc id filter" />
        <button className="btn btn-accent" onClick={load}>Apply</button>
      </div>
      {error && <p className="form-error mt-3">{error}</p>}
      <p className="table-note">{total} contradictions (NLI is imperfect — review each).</p>
      <div className="table-shell">
        <table className="w-full text-sm">
          <thead>
            <tr className="text-left">
              <th>A vs B</th>
              <th>Severity</th>
              <th>Conf</th>
              <th>Summary</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((r) => (
              <>
                <tr key={r.id} className="cursor-pointer" onClick={() => expand(r.id)}>
                  <td className="mono-n">{r.doc_a} vs {r.doc_b}</td>
                  <td><span className={r.severity === 'fundamental' ? 'chip chip-accent' : 'chip'}>{r.severity}</span></td>
                  <td className="mono-n">{r.confidence.toFixed(2)}</td>
                  <td>{r.summary}</td>
                </tr>
                {open[r.id] && (
                  <tr key={`${r.id}-d`} className="bg-amberbg">
                    <td colSpan={4}>
                      <div className="grid gap-3 md:grid-cols-2">
                        <p><mark>{open[r.id].claim_a}</mark></p>
                        <p><mark>{open[r.id].claim_b}</mark></p>
                      </div>
                      <p className="mt-3 text-sm opacity-80">{open[r.id].explanation}</p>
                    </td>
                  </tr>
                )}
              </>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
