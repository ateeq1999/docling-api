import { useState } from "react";
import "./App.css";

const API_BASE = "http://localhost:8000";

type OutputFormat = "text" | "markdown" | "json";

interface BulkResult {
  filename: string;
  status: "success" | "error";
  content?: string;
  error?: string;
}

interface ImageInfo {
  type: string;
  page: number;
  index?: number;
  width: number;
  height: number;
  path: string;
}

function App() {
  const [file, setFile] = useState<File | null>(null);
  const [files, setFiles] = useState<FileList | null>(null);
  const [format, setFormat] = useState<OutputFormat>("markdown");
  const [result, setResult] = useState<string>("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");
  const [healthStatus, setHealthStatus] = useState<string>("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleMultipleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(e.target.files);
    }
  };

  const clearResults = () => {
    setResult("");
    setError("");
  };

  const processDocument = async () => {
    if (!file) return;
    clearResults();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${API_BASE}/documents/process?format=${format}`,
        { method: "POST", body: formData }
      );

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Processing failed");
      }

      const text = await response.text();
      setResult(text);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const processStream = async () => {
    if (!file) return;
    clearResults();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${API_BASE}/documents/process/stream?format=${format}`,
        { method: "POST", body: formData }
      );

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Streaming failed");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let content = "";

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        content += decoder.decode(value, { stream: true });
        setResult(content);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const processStreamPages = async () => {
    if (!file) return;
    clearResults();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${API_BASE}/documents/process/stream/pages?format=${format}`,
        { method: "POST", body: formData }
      );

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Page streaming failed");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let content = "";

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        content += chunk;
        setResult(content);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const processSSE = async () => {
    if (!file) return;
    clearResults();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(
        `${API_BASE}/documents/process/sse?format=${format}`,
        { method: "POST", body: formData }
      );

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "SSE failed");
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();
      let content = "";

      while (reader) {
        const { done, value } = await reader.read();
        if (done) break;
        content += decoder.decode(value, { stream: true });
        setResult(content);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const processBulk = async () => {
    if (!files || files.length === 0) return;
    clearResults();
    setLoading(true);

    try {
      const formData = new FormData();
      Array.from(files).forEach((f) => formData.append("files", f));

      const response = await fetch(
        `${API_BASE}/documents/process/bulk?format=${format}`,
        { method: "POST", body: formData }
      );

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Bulk processing failed");
      }

      const results: BulkResult[] = await response.json();
      setResult(JSON.stringify(results, null, 2));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const extractImages = async () => {
    if (!file) return;
    clearResults();
    setLoading(true);

    try {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/images/extract`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const err = await response.json();
        throw new Error(err.detail || "Image extraction failed");
      }

      const data: { count: number; images: ImageInfo[] } = await response.json();
      setResult(JSON.stringify(data, null, 2));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Unknown error");
    } finally {
      setLoading(false);
    }
  };

  const checkHealth = async () => {
    try {
      const [liveRes, readyRes, rootRes] = await Promise.all([
        fetch(`${API_BASE}/health/live`),
        fetch(`${API_BASE}/health/ready`),
        fetch(`${API_BASE}/`),
      ]);

      const live = await liveRes.json();
      const ready = await readyRes.json();
      const root = await rootRes.json();

      setHealthStatus(
        `Live: ${live.status} | Ready: ${ready.status} | API: ${root.name} v${root.version}`
      );
    } catch {
      setHealthStatus("API unreachable");
    }
  };

  return (
    <div className="container">
      <h1>📄 Docling API Tester</h1>

      <section className="health-section">
        <button onClick={checkHealth} className="health-btn">
          Check API Health
        </button>
        {healthStatus && <span className="health-status">{healthStatus}</span>}
      </section>

      <section className="upload-section">
        <h2>Single File Processing</h2>
        <input type="file" onChange={handleFileChange} accept=".pdf,.docx,.pptx,.xlsx,.html,.png,.jpg,.jpeg" />
        {file && <span className="file-name">{file.name}</span>}

        <div className="format-select">
          <label>Output Format:</label>
          <select value={format} onChange={(e) => setFormat(e.target.value as OutputFormat)}>
            <option value="markdown">Markdown</option>
            <option value="text">Text</option>
            <option value="json">JSON</option>
          </select>
        </div>

        <div className="button-group">
          <button onClick={processDocument} disabled={!file || loading}>
            Process
          </button>
          <button onClick={processStream} disabled={!file || loading}>
            Stream
          </button>
          <button onClick={processStreamPages} disabled={!file || loading}>
            Stream Pages
          </button>
          <button onClick={processSSE} disabled={!file || loading}>
            SSE
          </button>
          <button onClick={extractImages} disabled={!file || loading}>
            Extract Images
          </button>
        </div>
      </section>

      <section className="upload-section">
        <h2>Bulk Processing</h2>
        <input type="file" onChange={handleMultipleFilesChange} multiple accept=".pdf,.docx,.pptx,.xlsx,.html,.png,.jpg,.jpeg" />
        {files && <span className="file-name">{files.length} files selected</span>}
        <button onClick={processBulk} disabled={!files || loading}>
          Process Bulk
        </button>
      </section>

      {loading && <div className="loading">Processing...</div>}

      {error && <div className="error">{error}</div>}

      {result && (
        <section className="result-section">
          <h2>Result</h2>
          <pre className="result">{result}</pre>
        </section>
      )}
    </div>
  );
}

export default App;
