import { useAppStore } from "../../lib/store";
import { useExtractImages } from "./use-images";
import styles from "../documents/DocumentProcessor.module.css";

export function ImageExtractor() {
  const { file, isStreaming } = useAppStore();
  const extractMutation = useExtractImages();

  const isLoading = extractMutation.isPending || isStreaming;

  return (
    <button
      onClick={() => file && extractMutation.mutate(file)}
      disabled={!file || isLoading}
      className={styles.button}
    >
      Extract Images
    </button>
  );
}
