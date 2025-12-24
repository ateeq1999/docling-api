import { create } from "zustand";
import type { OutputFormat } from "./api";

interface AppState {
  file: File | null;
  files: FileList | null;
  format: OutputFormat;
  result: string;
  isStreaming: boolean;

  setFile: (file: File | null) => void;
  setFiles: (files: FileList | null) => void;
  setFormat: (format: OutputFormat) => void;
  setResult: (result: string) => void;
  appendResult: (chunk: string) => void;
  clearResult: () => void;
  setIsStreaming: (isStreaming: boolean) => void;
}

export const useAppStore = create<AppState>((set) => ({
  file: null,
  files: null,
  format: "markdown",
  result: "",
  isStreaming: false,

  setFile: (file) => set({ file }),
  setFiles: (files) => set({ files }),
  setFormat: (format) => set({ format }),
  setResult: (result) => set({ result }),
  appendResult: (chunk) => set((state) => ({ result: state.result + chunk })),
  clearResult: () => set({ result: "" }),
  setIsStreaming: (isStreaming) => set({ isStreaming }),
}));
