import { useQuery } from "@tanstack/react-query";
import { FileText, CheckCircle, XCircle, HardDrive } from "lucide-react";
import { api } from "../lib/api";

interface Stats {
  total_documents: number;
  successful: number;
  failed: number;
  total_size_bytes: number;
  success_rate: number;
}

export function DashboardPage() {
  const { data: stats, isLoading } = useQuery<Stats>({
    queryKey: ["stats"],
    queryFn: async () => {
      const res = await fetch("http://localhost:8000/history/stats");
      return res.json();
    },
    refetchInterval: 5000,
  });

  const { data: health } = useQuery({
    queryKey: ["health"],
    queryFn: async () => {
      const [live, ready, root] = await Promise.all([
        api.health.live(),
        api.health.ready(),
        api.health.root(),
      ]);
      return { live, ready, root };
    },
  });

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 B";
    const k = 1024;
    const sizes = ["B", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  return (
    <div>
      <h1 className="text-3xl font-bold text-white mb-8">Dashboard</h1>

      {/* API Status */}
      {health && (
        <div className="mb-8 p-4 bg-slate-900 rounded-xl border border-slate-800">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500" />
              <span className="text-slate-300">
                {health.root.name} v{health.root.version}
              </span>
            </div>
            <span className="text-slate-600">|</span>
            <span className="text-slate-400">
              Live: {health.live.status} | Ready: {health.ready.status}
            </span>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Total Documents"
          value={isLoading ? "..." : stats?.total_documents ?? 0}
          icon={FileText}
          color="blue"
        />
        <StatCard
          title="Successful"
          value={isLoading ? "..." : stats?.successful ?? 0}
          icon={CheckCircle}
          color="green"
        />
        <StatCard
          title="Failed"
          value={isLoading ? "..." : stats?.failed ?? 0}
          icon={XCircle}
          color="red"
        />
        <StatCard
          title="Total Size"
          value={isLoading ? "..." : formatBytes(stats?.total_size_bytes ?? 0)}
          icon={HardDrive}
          color="purple"
        />
      </div>

      {/* Success Rate */}
      {stats && stats.total_documents > 0 && (
        <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
          <h2 className="text-lg font-semibold text-white mb-4">Success Rate</h2>
          <div className="flex items-center gap-4">
            <div className="flex-1 bg-slate-800 rounded-full h-4 overflow-hidden">
              <div
                className="h-full bg-emerald-500 transition-all duration-500"
                style={{ width: `${stats.success_rate}%` }}
              />
            </div>
            <span className="text-2xl font-bold text-emerald-500">
              {stats.success_rate}%
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({
  title,
  value,
  icon: Icon,
  color,
}: {
  title: string;
  value: string | number;
  icon: React.ElementType;
  color: "blue" | "green" | "red" | "purple";
}) {
  const colors = {
    blue: "bg-blue-500/10 text-blue-500 border-blue-500/20",
    green: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
    red: "bg-rose-500/10 text-rose-500 border-rose-500/20",
    purple: "bg-purple-500/10 text-purple-500 border-purple-500/20",
  };

  return (
    <div className="bg-slate-900 rounded-xl border border-slate-800 p-6">
      <div className="flex items-center gap-4">
        <div className={`p-3 rounded-lg border ${colors[color]}`}>
          <Icon className="w-6 h-6" />
        </div>
        <div>
          <p className="text-slate-400 text-sm">{title}</p>
          <p className="text-2xl font-bold text-white">{value}</p>
        </div>
      </div>
    </div>
  );
}
