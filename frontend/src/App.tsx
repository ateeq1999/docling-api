import { QueryClientProvider } from "@tanstack/react-query";
import { queryClient } from "./lib/query-client";
import { HealthCheck } from "./features/health/HealthCheck";
import { DocumentProcessor } from "./features/documents/DocumentProcessor";
import { BulkProcessor } from "./features/documents/BulkProcessor";
import { ImageExtractor } from "./features/images/ImageExtractor";
import { ResultDisplay } from "./components/ResultDisplay";
import { useAppStore } from "./lib/store";
import "./App.css";

function AppContent() {
  const { file, isStreaming } = useAppStore();

  return (
    <div className="container">
      <h1>📄 Docling API Tester</h1>

      <HealthCheck />

      <DocumentProcessor />

      <section className="extras-section">
        <h2>Additional Actions</h2>
        <div className="button-group">
          <ImageExtractor />
        </div>
        {!file && <p className="hint">Select a file above to enable image extraction</p>}
      </section>

      <BulkProcessor />

      {isStreaming && <div className="loading">Processing...</div>}

      <ResultDisplay />
    </div>
  );
}

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AppContent />
    </QueryClientProvider>
  );
}

export default App;
