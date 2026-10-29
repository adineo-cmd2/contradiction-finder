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
    const snippets = flags.map((f) => f.snippet).filter(Boolean);
    if (!snippets.length) return text;
    const escaped = snippets.map((s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'));
    const pattern = new RegExp(`(${escaped.join('|')})`, 'g');
    const marked = new Set(snippets);
    return text.split(pattern).map((part, i) =>
      marked.has(part) ? (
        <mark key={i} className="bg-amberbg">{part}</mark>
      ) : (
        <span key={i}>{part}</span>
      ),
    );
  }

  return (
    <div className="case-form">
      <div className="case-panel" style={{ marginTop: 0 }}>
        <div className="flex flex-wrap gap-2">
          <input className="input flex-1" value={id} onChange={(e) => setId(e.target.value)} placeholder="Document id" />
          <button className="btn btn-accent" onClick={load}>Open</button>
        </div>
      </div>
      {name && (
        <article className="document-sheet">
          <p className="label-x">Source file</p>
          <h2 className="document-title">{name}</h2>
          <p className="document-text">{render()}</p>
        </article>
      )}
    </div>
  );
}
