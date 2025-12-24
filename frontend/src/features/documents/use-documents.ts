import { useMutation } from "@tanstack/react-query";
import { api, type OutputFormat } from "../../lib/api";
import { useAppStore } from "../../lib/store";

export function useProcessDocument() {
  const { clearResult, setResult } = useAppStore();

  return useMutation({
    mutationFn: ({ file, format }: { file: File; format: OutputFormat }) =>
      api.documents.process(file, format),
    onMutate: () => clearResult(),
    onSuccess: (data) => setResult(data),
  });
}

export function useProcessStream() {
  const { clearResult, appendResult, setIsStreaming } = useAppStore();

  const mutation = useMutation({
    mutationFn: async ({ file, format }: { file: File; format: OutputFormat }) => {
      clearResult();
      setIsStreaming(true);

      try {
        for await (const chunk of api.documents.processStream(file, format)) {
          appendResult(chunk);
        }
      } finally {
        setIsStreaming(false);
      }
    },
  });

  return mutation;
}

export function useProcessStreamPages() {
  const { clearResult, appendResult, setIsStreaming } = useAppStore();

  return useMutation({
    mutationFn: async ({ file, format }: { file: File; format: OutputFormat }) => {
      clearResult();
      setIsStreaming(true);

      try {
        for await (const chunk of api.documents.processStreamPages(file, format)) {
          appendResult(chunk);
        }
      } finally {
        setIsStreaming(false);
      }
    },
  });
}

export function useProcessSSE() {
  const { clearResult, appendResult, setIsStreaming } = useAppStore();

  return useMutation({
    mutationFn: async ({ file, format }: { file: File; format: OutputFormat }) => {
      clearResult();
      setIsStreaming(true);

      try {
        for await (const chunk of api.documents.processSSE(file, format)) {
          appendResult(chunk);
        }
      } finally {
        setIsStreaming(false);
      }
    },
  });
}

export function useProcessBulk() {
  const { clearResult, setResult } = useAppStore();

  return useMutation({
    mutationFn: ({ files, format }: { files: FileList; format: OutputFormat }) =>
      api.documents.processBulk(files, format),
    onMutate: () => clearResult(),
    onSuccess: (data) => setResult(JSON.stringify(data, null, 2)),
  });
}
