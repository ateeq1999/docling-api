import { QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import { queryClient } from "./lib/query-client";
import { DashboardLayout } from "./layouts/DashboardLayout";
import { DashboardPage } from "./pages/DashboardPage";
import { ProcessPage } from "./pages/ProcessPage";
import { BulkPage } from "./pages/BulkPage";
import { ImagesPage } from "./pages/ImagesPage";
import { HistoryPage } from "./pages/HistoryPage";
import "./index.css";

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<DashboardLayout />}>
            <Route index element={<DashboardPage />} />
            <Route path="process" element={<ProcessPage />} />
            <Route path="bulk" element={<BulkPage />} />
            <Route path="images" element={<ImagesPage />} />
            <Route path="history" element={<HistoryPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  );
}

export default App;
