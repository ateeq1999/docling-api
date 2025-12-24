import { useAppStore } from "../../lib/store";
import { useProcessBulk } from "./use-documents";
import styles from "./DocumentProcessor.module.css";

export function BulkProcessor() {
  const { files, format, setFiles, isStreaming } = useAppStore();
  const bulkMutation = useProcessBulk();

  const isLoading = bulkMutation.isPending || isStreaming;

  const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(e.target.files);
    }
  };

  return (
    <section className={styles.section}>
      <h2>Bulk Processing</h2>

      <input
        type="file"
        onChange={handleFilesChange}
        multiple
        accept=".pdf,.docx,.pptx,.xlsx,.html,.png,.jpg,.jpeg"
        className={styles.fileInput}
      />
      {files && <span className={styles.fileName}>{files.length} files selected</span>}

      <button
        onClick={() => files && bulkMutation.mutate({ files, format })}
        disabled={!files || isLoading}
        className={styles.button}
      >
        Process Bulk
      </button>

      {bulkMutation.error && <div className={styles.error}>{bulkMutation.error.message}</div>}
    </section>
  );
}
