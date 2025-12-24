import { useAppStore } from "../../lib/store";
import type { OutputFormat } from "../../lib/api";
import {
  useProcessDocument,
  useProcessStream,
  useProcessStreamPages,
  useProcessSSE,
} from "./use-documents";
import styles from "./DocumentProcessor.module.css";

export function DocumentProcessor() {
  const { file, format, setFile, setFormat, isStreaming } = useAppStore();

  const processMutation = useProcessDocument();
  const streamMutation = useProcessStream();
  const streamPagesMutation = useProcessStreamPages();
  const sseMutation = useProcessSSE();

  const isLoading =
    processMutation.isPending ||
    streamMutation.isPending ||
    streamPagesMutation.isPending ||
    sseMutation.isPending ||
    isStreaming;

  const error =
    processMutation.error ||
    streamMutation.error ||
    streamPagesMutation.error ||
    sseMutation.error;

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <section className={styles.section}>
      <h2>Single File Processing</h2>

      <input
        type="file"
        onChange={handleFileChange}
        accept=".pdf,.docx,.pptx,.xlsx,.html,.png,.jpg,.jpeg"
        className={styles.fileInput}
      />
      {file && <span className={styles.fileName}>{file.name}</span>}

      <div className={styles.formatSelect}>
        <label>Output Format:</label>
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value as OutputFormat)}
          className={styles.select}
        >
          <option value="markdown">Markdown</option>
          <option value="text">Text</option>
          <option value="json">JSON</option>
        </select>
      </div>

      <div className={styles.buttonGroup}>
        <button
          onClick={() => file && processMutation.mutate({ file, format })}
          disabled={!file || isLoading}
          className={styles.button}
        >
          Process
        </button>
        <button
          onClick={() => file && streamMutation.mutate({ file, format })}
          disabled={!file || isLoading}
          className={styles.button}
        >
          Stream
        </button>
        <button
          onClick={() => file && streamPagesMutation.mutate({ file, format })}
          disabled={!file || isLoading}
          className={styles.button}
        >
          Stream Pages
        </button>
        <button
          onClick={() => file && sseMutation.mutate({ file, format })}
          disabled={!file || isLoading}
          className={styles.button}
        >
          SSE
        </button>
      </div>

      {error && <div className={styles.error}>{error.message}</div>}
    </section>
  );
}
