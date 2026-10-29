import { useEffect, useState } from 'react';
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

  useEffect(() => {
    refresh();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

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
    <div className="case-form" onMouseEnter={refresh}>
      <div className="flex flex-col gap-2 sm:flex-row">
        <input
          className="input flex-1"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="New corpus name, e.g. Climate policy review"
        />
        <button className="btn btn-accent" onClick={create}>Open a case</button>
        <button className="btn btn-ghost" onClick={refresh}>Refresh</button>
      </div>
      {error && <p className="form-error">{error}</p>}
      <div>
        <p className="label-x">Cases on file</p>
        <ul>
          {corpora.map((c) => (
            <li key={c.id} className="flex items-center justify-between gap-3">
              <button onClick={() => setCorpusId(c.id)}>{c.name}</button>
              <span className="mono-n text-xs opacity-70">
                {c.docs} docs · {c.analysed ? 'analysed' : 'not analysed'}
                {corpusId === c.id ? ' · selected' : ''}
              </span>
            </li>
          ))}
          {corpora.length === 0 && (
            <li className="mono-n text-xs opacity-70">No cases on file yet.</li>
          )}
        </ul>
      </div>
      {corpusId != null && (
        <div>
          <p className="label-x">Add a document</p>
          <label className="upload-drop">
            <strong>Drop files here or click to upload</strong>
            .txt .md .pdf .docx
            <input
              type="file"
              multiple
              className="hidden"
              onChange={(e) => upload(e.target.files)}
            />
          </label>
        </div>
      )}
      <ul className="space-y-1 text-sm">
        {Object.entries(states).map(([k, v]) => (
          <li key={k} className="mono-n">{k.split('-').slice(0, -1).join('-')}: {v}</li>
        ))}
      </ul>
    </div>
  );
}
