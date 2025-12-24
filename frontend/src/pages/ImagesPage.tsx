import { useState } from "react";
import { Image, Loader2 } from "lucide-react";
import { useAppStore } from "../lib/store";
import { useExtractImages } from "../features/images/use-images";
import type { ImageInfo } from "../lib/api";

export function ImagesPage() {
  const { file, result, setFile } = useAppStore();
  const [dragOver, setDragOver] = useState(false);
  const extractMutation = useExtractImages();

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

  let parsedResult: { count: number; images: ImageInfo[] } | null = null;
  try {
    if (result) {
      parsedResult = JSON.parse(result);
    }
  } catch {
    parsedResult = null;
  }

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-8">Extract Images</h1>

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
          id="image-file-upload"
          className="hidden"
          onChange={handleFileChange}
          accept=".pdf,.docx,.pptx"
        />
        <label htmlFor="image-file-upload" className="cursor-pointer">
          <Image className="w-12 h-12 text-slate-500 mx-auto mb-4" />
          <p className="text-slate-300 mb-2">
            Upload a document to extract images
          </p>
          <p className="text-slate-500 text-sm">
            Supports PDF, DOCX, and PPTX files
          </p>
        </label>
      </div>

      {/* Selected File */}
      {file && (
        <div className="mt-6 flex items-center gap-4">
          <div className="flex-1 p-4 bg-slate-900 rounded-xl border border-slate-800 flex items-center gap-4">
            <Image className="w-10 h-10 text-purple-500" />
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

          <button
            onClick={() => file && extractMutation.mutate(file)}
            disabled={!file || extractMutation.isPending}
            className="px-6 py-4 bg-purple-500 text-white rounded-xl font-medium hover:bg-purple-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
          >
            {extractMutation.isPending && <Loader2 className="w-4 h-4 animate-spin" />}
            Extract Images
          </button>
        </div>
      )}

      {/* Error */}
      {extractMutation.error && (
        <div className="mt-6 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl text-rose-400">
          {extractMutation.error.message}
        </div>
      )}

      {/* Results */}
      {parsedResult && (
        <div className="mt-8">
          <h2 className="text-lg font-semibold text-white mb-4">
            Found {parsedResult.count} image{parsedResult.count !== 1 ? "s" : ""}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {parsedResult.images.map((img, i) => (
              <div
                key={i}
                className="bg-slate-900 border border-slate-800 rounded-xl p-4"
              >
                <div className="flex items-center gap-2 mb-3">
                  <span
                    className={`text-xs px-2 py-1 rounded ${
                      img.type === "embedded"
                        ? "bg-blue-500/10 text-blue-500"
                        : "bg-purple-500/10 text-purple-500"
                    }`}
                  >
                    {img.type}
                  </span>
                  <span className="text-slate-500 text-sm">Page {img.page}</span>
                </div>
                <div className="text-slate-400 text-sm space-y-1">
                  <p>
                    Size: {img.width} × {img.height}
                  </p>
                  {img.index && <p>Index: {img.index}</p>}
                  <p className="truncate text-slate-600" title={img.path}>
                    {img.path}
                  </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
