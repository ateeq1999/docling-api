import { useState } from "react";
import { Upload, Files, Loader2, CheckCircle, XCircle } from "lucide-react";
import { useAppStore } from "../lib/store";
import type { OutputFormat, BulkResult } from "../lib/api";
import { useProcessBulk } from "../features/documents/use-documents";

export function BulkPage() {
  const { files, format, result, setFiles, setFormat } = useAppStore();
  const [dragOver, setDragOver] = useState(false);
  const bulkMutation = useProcessBulk();

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.length) {
      setFiles(e.dataTransfer.files);
    }
  };

  const handleFilesChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.length) {
      setFiles(e.target.files);
    }
  };

  const parsedResults: BulkResult[] = result ? JSON.parse(result) : [];

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-8">Bulk Processing</h1>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-xl p-12 text-center transition-colors ${
          dragOver
            ? "border-rose-500 bg-rose-500/10"
            : "border-slate-700 hover:border-slate-600"
        }`}
        onDragOver={(e) => {
          e.preventDefault();
          setDragOver(true);
        }}
        onDragLeave={() => setDragOver(false)}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="files-upload"
          className="hidden"
          onChange={handleFilesChange}
          multiple
          accept=".pdf,.docx,.pptx,.xlsx,.html,.png,.jpg,.jpeg"
        />
        <label htmlFor="files-upload" className="cursor-pointer">
          <Files className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className="text-slate-300 mb-2">
            Drag and drop multiple files, or click to browse
          </p>
          <p className="text-slate-500 text-sm">
            Process multiple documents at once
          </p>
        </label>
      </div>

      {/* Selected Files */}
      {files && files.length > 0 && (
        <div className="mt-6 p-4 bg-slate-900 rounded-xl border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <p className="text-white font-medium">
              {files.length} file{files.length > 1 ? "s" : ""} selected
            </p>
            <button
              onClick={() => setFiles(null)}
              className="text-slate-500 hover:text-white text-sm"
            >
              Clear all
            </button>
          </div>
          <div className="space-y-2 max-h-40 overflow-auto">
            {Array.from(files).map((file, i) => (
              <div key={i} className="flex items-center gap-2 text-sm text-slate-400">
                <Upload className="w-4 h-4" />
                {file.name}
                <span className="text-slate-600">
                  ({(file.size / 1024 / 1024).toFixed(2)} MB)
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Format & Process */}
      <div className="mt-6 flex items-center gap-4">
        <span className="text-slate-400">Output Format:</span>
        <select
          value={format}
          onChange={(e) => setFormat(e.target.value as OutputFormat)}
          className="bg-slate-800 border border-slate-700 text-white rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-rose-500"
        >
          <option value="markdown">Markdown</option>
          <option value="text">Plain Text</option>
          <option value="json">JSON</option>
        </select>

        <button
          onClick={() => files && bulkMutation.mutate({ files, format })}
          disabled={!files || bulkMutation.isPending}
          className="px-6 py-2 bg-rose-500 text-white rounded-lg font-medium hover:bg-rose-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
        >
          {bulkMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
          Process All
        </button>
      </div>

      {/* Error */}
      {bulkMutation.error && (
        <div className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400">
          {bulkMutation.error.message}
        </div>
      )}

      {/* Results */}
      {parsedResults.length > 0 && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-white mb-4">Results</h2>
          <div className="space-y-4">
            {parsedResults.map((res, i) => (
              <div
                key={i}
                className="bg-slate-900 border border-slate-800 rounded-xl p-4"
              >
                <div className="flex items-center gap-3 mb-3">
                  {res.status === "success" ? (
                    <CheckCircle className="w-5 h-5 text-emerald-500" />
                  ) : (
                    <XCircle className="w-5 h-5 text-rose-500" />
                  )}
                  <span className="text-white font-medium">{res.filename}</span>
                  <span
                    className={`text-sm px-2 py-0.5 rounded ${
                      res.status === "success"
                        ? "bg-emerald-500/10 text-emerald-500"
                        : "bg-rose-500/10 text-rose-500"
                    }`}
                  >
                    {res.status}
                  </span>
                </div>
                {res.error && <p className="text-rose-400 text-sm">{res.error}</p>}
                {res.content && (
                  <pre className="mt-2 p-3 bg-slate-950 rounded-lg text-slate-400 text-sm overflow-auto max-h-40 whitespace-pre-wrap">
                    {res.content.slice(0, 500)}
                    {res.content.length > 500 && "..."}
                  </pre>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
