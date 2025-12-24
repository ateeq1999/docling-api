import { useAppStore } from "../lib/store";
import styles from "./ResultDisplay.module.css";

export function ResultDisplay() {
  const { result, isStreaming } = useAppStore();

  if (!result && !isStreaming) return null;

  return (
    <section className={styles.section}>
      <h2>
        Result
        {isStreaming && <span className={styles.streaming}> (streaming...)</span>}
      </h2>
      <pre className={styles.result}>{result}</pre>
    </section>
  );
}
