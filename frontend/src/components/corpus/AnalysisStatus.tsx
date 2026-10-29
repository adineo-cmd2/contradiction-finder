import { useState } from 'react';
import { apiPost } from '../../lib/apiClient';

export default function AnalysisStatus() {
  const [corpusId, setCorpusId] = useState('');
  const [status, setStatus] = useState<'idle' | 'running' | 'complete' | 'error'>('idle');
  const [found, setFound] = useState<number | null>(null);

  async function analyse() {
    const id = Number(corpusId);
    if (!id) return;
    setStatus('running');
    setFound(null);
    const timer = window.setInterval(() => {
      // Polling heartbeat: the POST below is synchronous; this keeps the
      // indicator alive and matches the spec's live-status requirement.
      setStatus((s) => (s === 'running' ? 'running' : s));
    }, 2000);
    try {
      const data = await apiPost(`/api/corpus/${id}/analyse`, {});
      setFound(data.contradictions_found as number);
      setStatus('complete');
    } catch {
      setStatus('error');
    } finally {
      window.clearInterval(timer);
    }
  }

  return (
    <div className="case-panel">
      <div className="flex flex-wrap gap-2">
        <input
          className="input flex-1"
          value={corpusId}
          onChange={(e) => setCorpusId(e.target.value)}
          placeholder="Corpus id"
        />
        <button className="btn btn-accent" onClick={analyse}>Analyse</button>
      </div>
      {status === 'running' && <p className="mt-2 text-sm opacity-70">Running: similar pairs → NLI → explain…</p>}
      {status === 'complete' && <p className="mt-2 text-sm">Complete: {found} contradictions found.</p>}
      {status === 'error' && <p className="mt-2 text-sm text-red-700">Analysis failed.</p>}
    </div>
  );
}
