import React from 'react';
import { Users, LayoutDashboard, Truck, MessageSquare, Database } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

import { Search, BarChart2, ShieldAlert, Smile, TrendingUp, AlertCircle } from 'lucide-react';

interface SidebarProps {
  currentRole: string;
  setRole: (role: string) => void;
  onQueryClick?: (query: string) => void;
}

const Sidebar: React.FC<SidebarProps> = ({ currentRole, setRole, onQueryClick }) => {
  const roles = [
    { id: 'ProductOwner', name: 'Product Owner', icon: LayoutDashboard },
    { id: 'ScrumMaster', name: 'Scrum Master', icon: Users },
    { id: 'DeliveryLead', name: 'Delivery Lead', icon: Truck },
  ];

  const quickQueries = [
    { text: "Epics blocked by UAT failures", icon: AlertCircle },
    { text: "Generate health reports per epic", icon: BarChart2 },
    { text: "Detect usual delays or defect spikes", icon: ShieldAlert },
    { text: "Analyze developer morale sentiment", icon: Smile },
    { text: "Show completion velocity trends", icon: TrendingUp },
  ];

  return (
    <div className="w-64 bg-slate-900 text-white h-screen flex flex-col fixed left-0 top-0">
      <div className="p-6 text-xl font-bold border-b border-slate-800">
        Agile AI Agent
      </div>
      <nav className="flex-1 mt-6 overflow-y-auto">
        <div className="px-6 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Roles
        </div>
        {roles.map((role) => {
          const Icon = role.icon;
          return (
            <button
              key={role.id}
              onClick={() => setRole(role.id)}
              className={cn(
                "w-full flex items-center px-6 py-3 transition-colors",
                currentRole === role.id
                  ? "bg-blue-600 text-white"
                  : "text-slate-400 hover:bg-slate-800 hover:text-white"
              )}
            >
              <Icon className="w-5 h-5 mr-3" />
              {role.name}
            </button>
          );
        })}

        <div className="px-6 mt-8 mb-2 text-xs font-semibold text-slate-500 uppercase tracking-wider">
          Quick Insights
        </div>
        {quickQueries.map((query, idx) => {
          const Icon = query.icon;
          return (
            <button
              key={idx}
              onClick={() => onQueryClick && onQueryClick(query.text)}
              className="w-full flex items-center px-6 py-3 text-slate-400 hover:bg-slate-800 hover:text-white transition-colors text-sm text-left"
            >
              <Icon className="w-4 h-4 mr-3" />
              {query.text}
            </button>
          );
        })}
      </nav>
      <div className="p-6 border-t border-slate-800 text-xs text-slate-500">
        Powered by Google Gemini
      </div>
    </div>
  );
};

export default Sidebar;
