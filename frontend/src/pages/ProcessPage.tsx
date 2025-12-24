import { useState } from "react";
import { Upload, FileText, Loader2 } from "lucide-react";
import { useAppStore } from "../lib/store";
import type { OutputFormat } from "../lib/api";
import {
  useProcessDocument,
  useProcessStream,
  useProcessStreamPages,
  useProcessSSE,
} from "../features/documents/use-documents";

export function ProcessPage() {
  const { file, format, result, setFile, setFormat, isStreaming } = useAppStore();
  const [dragOver, setDragOver] = useState(false);

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

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(false);
    if (e.dataTransfer.files?.[0]) {
      setFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) {
      setFile(e.target.files[0]);
    }
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-8">Process Document</h1>

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
          id="file-upload"
          className="hidden"
          onChange={handleFileChange}
          accept=".pdf,.docx,.pptx,.xlsx,.html,.png,.jpg,.jpeg"
        />
        <label htmlFor="file-upload" className="cursor-pointer">
          <Upload className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className="text-slate-300 mb-2">
            Drag and drop a file here, or click to browse
          </p>
          <p className="text-slate-500 text-sm">
            Supports PDF, DOCX, PPTX, XLSX, HTML, and images
          </p>
        </label>
      </div>

      {/* Selected File */}
      {file && (
        <div className="mt-6 p-4 bg-slate-900 rounded-xl border border-slate-800 flex items-center gap-4">
          <FileText className="w-10 h-10 text-rose-500" />
          <div className="flex-1">
            <p className="text-white font-medium">{file.name}</p>
            <p className="text-slate-500 text-sm">
              {(file.size / 1024 / 1024).toFixed(2)} MB
            </p>
          </div>
          <button
            onClick={() => setFile(null)}
            className="text-slate-500 hover:text-white"
          >
            ✕
          </button>
        </div>
      )}

      {/* Format Selection */}
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
      </div>

      {/* Action Buttons */}
      <div className="mt-6 flex flex-wrap gap-3">
        <ActionButton
          onClick={() => file && processMutation.mutate({ file, format })}
          disabled={!file || isLoading}
          loading={processMutation.isPending}
        >
          Process
        </ActionButton>
        <ActionButton
          onClick={() => file && streamMutation.mutate({ file, format })}
          disabled={!file || isLoading}
          loading={streamMutation.isPending}
          variant="secondary"
        >
          Stream
        </ActionButton>
        <ActionButton
          onClick={() => file && streamPagesMutation.mutate({ file, format })}
          disabled={!file || isLoading}
          loading={streamPagesMutation.isPending}
          variant="secondary"
        >
          Stream Pages
        </ActionButton>
        <ActionButton
          onClick={() => file && sseMutation.mutate({ file, format })}
          disabled={!file || isLoading}
          loading={sseMutation.isPending}
          variant="secondary"
        >
          SSE
        </ActionButton>
      </div>

      {/* Error */}
      {error && (
        <div className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400">
          {error.message}
        </div>
      )}

      {/* Result */}
      {(result || isStreaming) && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
            Result
            {isStreaming && (
              <span className="text-sm text-amber-500 flex items-center gap-1">
                <Loader2 className="w-4 h-4 animate-spin" />
                Streaming...
              </span>
            )}
          </h2>
          <pre className="bg-slate-900 border border-slate-800 rounded-xl p-6 overflow-auto max-h-[500px] text-slate-300 text-sm font-mono whitespace-pre-wrap">
            {result}
          </pre>
        </div>
      )}
    </div>
  );
}

function ActionButton({
  children,
  onClick,
  disabled,
  loading,
  variant = "primary",
}: {
  children: React.ReactNode;
  onClick: () => void;
  disabled: boolean;
  loading?: boolean;
  variant?: "primary" | "secondary";
}) {
  const base =
    "px-6 py-3 rounded-lg font-medium transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed";
  const variants = {
    primary: "bg-rose-500 text-white hover:bg-rose-600",
    secondary: "bg-slate-800 text-white hover:bg-slate-700 border border-slate-700",
  };

  return (
    <button
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]}`}
    >
      {loading && <Loader2 className="w-4 h-4 animate-spin" />}
      {children}
    </button>
  );
}
