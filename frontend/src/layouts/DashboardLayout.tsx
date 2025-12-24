import { Link, Outlet, useLocation } from "react-router-dom";
import {
  FileText,
  FolderUp,
  Image,
  History,
  Activity,
  LayoutDashboard,
} from "lucide-react";

const navItems = [
  { path: "/", label: "Dashboard", icon: LayoutDashboard },
  { path: "/process", label: "Process Document", icon: FileText },
  { path: "/bulk", label: "Bulk Processing", icon: FolderUp },
  { path: "/images", label: "Extract Images", icon: Image },
  { path: "/history", label: "History", icon: History },
];

export function DashboardLayout() {
  const location = useLocation();

  return (
    <div className="flex h-screen bg-slate-950">
      {/* Sidebar */}
      <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col">
        <div className="p-6 border-b border-slate-800">
          <h1 className="text-xl font-bold text-white flex items-center gap-2">
            <FileText className="w-6 h-6 text-rose-500" />
            Docling API
          </h1>
        </div>

        <nav className="flex-1 p-4">
          <ul className="space-y-2">
            {navItems.map((item) => {
              const isActive = location.pathname === item.path;
              const Icon = item.icon;

              return (
                <li key={item.path}>
                  <Link
                    to={item.path}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive
                        ? "bg-rose-500/10 text-rose-500 border border-rose-500/20"
                        : "text-slate-400 hover:bg-slate-800 hover:text-white"
                    }`}
                  >
                    <Icon className="w-5 h-5" />
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </nav>

        <div className="p-4 border-t border-slate-800">
          <HealthIndicator />
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 overflow-auto">
        <div className="p-8">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

function HealthIndicator() {
  return (
    <div className="flex items-center gap-2 text-sm text-slate-500">
      <Activity className="w-4 h-4" />
      <span>API Status</span>
      <span className="ml-auto w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
    </div>
  );
}
