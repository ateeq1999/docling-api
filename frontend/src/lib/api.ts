export const API_BASE = "http://localhost:8000";

export type OutputFormat = "text" | "markdown" | "json";

export interface BulkResult {
  filename: string;
  status: "success" | "error";
  content?: string;
  error?: string;
}

export interface ImageInfo {
  type: string;
  page: number;
  index?: number;
  width: number;
  height: number;
  path: string;
}

export interface ImagesResponse {
  count: number;
  images: ImageInfo[];
}

export interface HealthResponse {
  status: string;
}

export interface RootResponse {
  name: string;
  version: string;
  docs: string;
}

export class ApiError extends Error {
  status: number;

  constructor(message: string, status: number) {
    super(message);
    this.name = "ApiError";
    this.status = status;
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(error.detail || "Request failed", response.status);
  }
  return response.json();
}

async function handleTextResponse(response: Response): Promise<string> {
  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: "Request failed" }));
    throw new ApiError(error.detail || "Request failed", response.status);
  }
  return response.text();
}

export const api = {
  health: {
    live: () => fetch(`${API_BASE}/health/live`).then((r) => handleResponse<HealthResponse>(r)),
    ready: () => fetch(`${API_BASE}/health/ready`).then((r) => handleResponse<HealthResponse>(r)),
    root: () => fetch(`${API_BASE}/`).then((r) => handleResponse<RootResponse>(r)),
  },

  documents: {
    process: (file: File, format: OutputFormat) => {
      const formData = new FormData();
      formData.append("file", file);
      return fetch(`${API_BASE}/documents/process?format=${format}`, {
        method: "POST",
        body: formData,
      }).then(handleTextResponse);
    },

    processStream: async function* (file: File, format: OutputFormat): AsyncGenerator<string> {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/documents/process/stream?format=${format}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Streaming failed" }));
        throw new ApiError(error.detail || "Streaming failed", response.status);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response body");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        yield decoder.decode(value, { stream: true });
      }
    },

    processStreamPages: async function* (file: File, format: OutputFormat): AsyncGenerator<string> {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/documents/process/stream/pages?format=${format}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "Page streaming failed" }));
        throw new ApiError(error.detail || "Page streaming failed", response.status);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response body");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        yield decoder.decode(value, { stream: true });
      }
    },

    processSSE: async function* (file: File, format: OutputFormat): AsyncGenerator<string> {
      const formData = new FormData();
      formData.append("file", file);

      const response = await fetch(`${API_BASE}/documents/process/sse?format=${format}`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: "SSE failed" }));
        throw new ApiError(error.detail || "SSE failed", response.status);
      }

      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) throw new Error("No response body");

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        yield decoder.decode(value, { stream: true });
      }
    },

    processBulk: (files: FileList, format: OutputFormat) => {
      const formData = new FormData();
      Array.from(files).forEach((f) => formData.append("files", f));
      return fetch(`${API_BASE}/documents/process/bulk?format=${format}`, {
        method: "POST",
        body: formData,
      }).then((r) => handleResponse<BulkResult[]>(r));
    },
  },

  images: {
    extract: (file: File) => {
      const formData = new FormData();
      formData.append("file", file);
      return fetch(`${API_BASE}/images/extract`, {
        method: "POST",
        body: formData,
      }).then((r) => handleResponse<ImagesResponse>(r));
    },
  },
};
