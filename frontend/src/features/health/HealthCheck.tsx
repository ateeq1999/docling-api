import { useHealthStatus } from "./use-health";
import styles from "./HealthCheck.module.css";

export function HealthCheck() {
  const { checkHealth, status, isLoading } = useHealthStatus();

  return (
    <section className={styles.section}>
      <button onClick={checkHealth} disabled={isLoading} className={styles.button}>
        {isLoading ? "Checking..." : "Check API Health"}
      </button>
      {status && <span className={styles.status}>{status}</span>}
    </section>
  );
}
