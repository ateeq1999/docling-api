import { useQuery } from "@tanstack/react-query";
import { FileText, CheckCircle, XCircle, Clock, Loader2 } from "lucide-react";

interface Document {
  id: number;
  filename: string;
  file_size: number;
  file_type: string;
  output_format: string;
  status: string;
  page_count: number | null;
  processing_time_ms: number | null;
  error_message: string | null;
  created_at: string;
}

export function HistoryPage() {
  const { data, isLoading, refetch, isFetching } = useQuery<{ documents: Document[] }>({
    queryKey: ["history"],
    queryFn: async () => {
      const res = await fetch("http://localhost:8000/history/?limit=100");
      return res.json();
    },
  });

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleString();
  };

  return (
    <div>
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-white">Processing History</h1>
        <button
          onClick={() => refetch()}
          disabled={isFetching}
          className="px-4 py-2 bg-slate-800 text-white rounded-lg hover:bg-slate-700 flex items-center gap-2 disabled:opacity-50"
        >
          {isFetching && <Loader2 className="w-4 h-4 animate-spin" />}
          Refresh
        </button>
      </div>

      {isLoading ? (
        <div className="flex items-center justify-center py-20">
          <Loader2 className="w-8 h-8 text-slate-500 animate-spin" />
        </div>
      ) : !data?.documents?.length ? (
        <div className="text-center py-20">
          <FileText className="w-16 h-16 text-slate-700 mx-auto mb-4" />
          <p className="text-slate-500">No documents processed yet</p>
          <p className="text-slate-600 text-sm">
            Process a document to see it here
          </p>
        </div>
      ) : (
        <div className="bg-slate-900 border border-slate-800 rounded-xl overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-slate-800">
                <th className="text-left p-4 text-slate-400 font-medium">File</th>
                <th className="text-left p-4 text-slate-400 font-medium">Type</th>
                <th className="text-left p-4 text-slate-400 font-medium">Size</th>
                <th className="text-left p-4 text-slate-400 font-medium">Format</th>
                <th className="text-left p-4 text-slate-400 font-medium">Status</th>
                <th className="text-left p-4 text-slate-400 font-medium">Time</th>
                <th className="text-left p-4 text-slate-400 font-medium">Date</th>
              </tr>
            </thead>
            <tbody>
              {data.documents.map((doc) => (
                <tr
                  key={doc.id}
                  className="border-b border-slate-800/50 hover:bg-slate-800/30"
                >
                  <td className="p-4">
                    <div className="flex items-center gap-3">
                      <FileText className="w-5 h-5 text-slate-500" />
                      <span className="text-white truncate max-w-[200px]" title={doc.filename}>
                        {doc.filename}
                      </span>
                    </div>
                  </td>
                  <td className="p-4">
                    <span className="px-2 py-1 bg-slate-800 text-slate-400 rounded text-sm uppercase">
                      {doc.file_type}
                    </span>
                  </td>
                  <td className="p-4 text-slate-400">{formatBytes(doc.file_size)}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 bg-blue-500/10 text-blue-400 rounded text-sm">
                      {doc.output_format}
                    </span>
                  </td>
                  <td className="p-4">
                    {doc.status === "success" ? (
                      <span className="flex items-center gap-2 text-emerald-500">
                        <CheckCircle className="w-4 h-4" />
                        Success
                      </span>
                    ) : (
                      <span className="flex items-center gap-2 text-rose-500" title={doc.error_message || ""}>
                        <XCircle className="w-4 h-4" />
                        Failed
                      </span>
                    )}
                  </td>
                  <td className="p-4 text-slate-400">
                    {doc.processing_time_ms ? (
                      <span className="flex items-center gap-1">
                        <Clock className="w-4 h-4" />
                        {(doc.processing_time_ms / 1000).toFixed(1)}s
                      </span>
                    ) : (
                      "-"
                    )}
                  </td>
                  <td className="p-4 text-slate-500 text-sm">
                    {formatDate(doc.created_at)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
