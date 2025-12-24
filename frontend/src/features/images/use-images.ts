import { useMutation } from "@tanstack/react-query";
import { api } from "../../lib/api";
import { useAppStore } from "../../lib/store";

export function useExtractImages() {
  const { clearResult, setResult } = useAppStore();

  return useMutation({
    mutationFn: (file: File) => api.images.extract(file),
    onMutate: () => clearResult(),
    onSuccess: (data) => setResult(JSON.stringify(data, null, 2)),
  });
}
