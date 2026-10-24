import { useState } from 'react';
import { apiGet, apiPost, apiUpload } from '../../lib/apiClient';

type FileStatus = 'uploading' | 'analysing' | 'done' | 'error';

interface Corpus {
  id: number;
  name: string;
  docs: number;
  analysed: boolean;
}

export default function UploadZone() {
  const [name, setName] = useState('');
  const [corpusId, setCorpusId] = useState<number | null>(null);
  const [corpora, setCorpora] = useState<Corpus[]>([]);
  const [states, setStates] = useState<Record<string, FileStatus>>({});
  const [error, setError] = useState('');

  async function refresh() {
    try {
      const data = await apiGet('/api/corpus');
      setCorpora(Array.isArray(data) ? data : data.corpora ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to load corpora.');
    }
  }

  async function create() {
    setError('');
    if (!name.trim()) {
      setError('Enter a corpus name.');
      return;
    }
    try {
      const data = await apiPost('/api/corpus', { name: name.trim() });
      setCorpusId(data.corpus_id as number);
      setName('');
      await refresh();
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed to create corpus.');
    }
  }

  async function upload(files: FileList | null) {
    if (!files || files.length === 0 || corpusId == null) return;
    for (const f of Array.from(files)) {
      const key = `${f.name}-${Date.now()}`;
      setStates((s) => ({ ...s, [key]: 'uploading' }));
      try {
        await apiUpload(`/api/corpus/${corpusId}/upload`, f);
        setStates((s) => ({ ...s, [key]: 'analysing' }));
        setStates((s) => ({ ...s, [key]: 'done' }));
      } catch {
        setStates((s) => ({ ...s, [key]: 'error' }));
      }
    }
    await refresh();
  }

  return (
    <div className="space-y-4" onMouseEnter={refresh}>
      <div className="flex gap-2">
        <input
          className="flex-1 border border-slate-300 px-2 py-1 text-slateink"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="New corpus name, e.g. Climate policy review"
        />
        <button className="border border-slate-300 px-3 py-1" onClick={create}>Create</button>
        <button className="underline" onClick={refresh}>Refresh</button>
      </div>
      {error && <p className="text-sm text-red-700">{error}</p>}
      <ul className="divide-y divide-slate-200 border border-slate-200">
        {corpora.map((c) => (
          <li key={c.id} className="flex items-center justify-between px-3 py-2">
            <button className="underline" onClick={() => setCorpusId(c.id)}>{c.name}</button>
            <span className="text-sm opacity-70">
              {c.docs} docs · {c.analysed ? 'analysed' : 'not analysed'}
              {corpusId === c.id ? ' · selected' : ''}
            </span>
          </li>
        ))}
      </ul>
      {corpusId != null && (
        <label className="block border border-dashed border-slate-300 p-6 text-center">
          Drop files here or click to upload (.txt .md .pdf .docx)
          <input
            type="file"
            multiple
            className="hidden"
            onChange={(e) => upload(e.target.files)}
          />
        </label>
      )}
      <ul className="space-y-1 text-sm">
        {Object.entries(states).map(([k, v]) => (
          <li key={k} className="mono-n">{k.split('-').slice(0, -1).join('-')}: {v}</li>
        ))}
      </ul>
    </div>
  );
}
