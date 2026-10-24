import { useEffect, useState } from 'react';
import { apiGet } from '../../lib/apiClient';

interface Flag {
  snippet: string;
  severity: string;
}

export default function DocumentView() {
  const [id, setId] = useState('');
  const [name, setName] = useState('');
  const [text, setText] = useState('');
  const [flags, setFlags] = useState<Flag[]>([]);

  async function load() {
    if (!id) return;
    const d = await apiGet(`/api/documents/${id}`);
    setName(d.filename as string);
    setText(d.text as string);
    setFlags((d.flags ?? []) as Flag[]);
  }

  useEffect(() => {
    const qid = new URLSearchParams(window.location.search).get('id') ?? '';
    setId(qid);
    if (qid) {
      apiGet(`/api/documents/${qid}`).then((d) => {
        setName(d.filename as string);
        setText(d.text as string);
        setFlags((d.flags ?? []) as Flag[]);
      });
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function render() {
    let out = text;
    for (const f of flags) {
      out = out.split(f.snippet).join(`\u0000${f.snippet}\u0001`);
    }
    return out.split('\u0000').map((part, i) =>
      part.includes('\u0001') ? (
        <mark key={i} className="bg-amberbg">{part.replace('\u0001', '')}</mark>
      ) : (
        <span key={i}>{part}</span>
      ),
    );
  }

  return (
    <div>
      <div className="flex gap-2">
        <input className="border border-slate-300 px-2 py-1" value={id} onChange={(e) => setId(e.target.value)} placeholder="Document id" />
        <button className="border border-slate-300 px-3 py-1" onClick={load}>Open</button>
      </div>
      <h2 className="serif-h mt-4 text-xl">{name}</h2>
      <p className="mt-2 whitespace-pre-wrap text-sm leading-6">{render()}</p>
    </div>
  );
}
