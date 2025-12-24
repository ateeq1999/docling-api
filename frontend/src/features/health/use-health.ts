import { useQuery } from "@tanstack/react-query";
import { api } from "../../lib/api";

export function useHealthStatus() {
  const liveQuery = useQuery({
    queryKey: ["health", "live"],
    queryFn: api.health.live,
    enabled: false,
  });

  const readyQuery = useQuery({
    queryKey: ["health", "ready"],
    queryFn: api.health.ready,
    enabled: false,
  });

  const rootQuery = useQuery({
    queryKey: ["health", "root"],
    queryFn: api.health.root,
    enabled: false,
  });

  const checkHealth = async () => {
    await Promise.all([liveQuery.refetch(), readyQuery.refetch(), rootQuery.refetch()]);
  };

  const isLoading = liveQuery.isFetching || readyQuery.isFetching || rootQuery.isFetching;

  const status =
    liveQuery.data && readyQuery.data && rootQuery.data
      ? `Live: ${liveQuery.data.status} | Ready: ${readyQuery.data.status} | API: ${rootQuery.data.name} v${rootQuery.data.version}`
      : liveQuery.error || readyQuery.error || rootQuery.error
        ? "API unreachable"
        : "";

  return { checkHealth, status, isLoading };
}
