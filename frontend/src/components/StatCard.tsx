import React from 'react';
import { Shield, Activity, Cpu, AlertTriangle, Database } from 'lucide-react';

const StatCard = ({ label, value, icon: Icon, color }: any) => {
  const colorMap = {
    blue: 'from-blue-500 to-blue-700',
    green: 'from-green-500 to-green-700',
    red: 'from-red-500 to-red-700',
    yellow: 'from-yellow-500 to-orange-600',
    purple: 'from-purple-500 to-purple-700',
  };

  return (
    <div className={`glass p-6 rounded-2xl flex flex-col gap-4 border border-white/10 shadow-xl transform hover:scale-105 transition-transform ${colorMap[color] || 'from-gray-700 to-gray-900'}`}>
      <div className="flex items-center justify-between">
        <span className="text-xs font-medium opacity-70">{label}</span>
        <div className={`p-2 rounded-lg bg-white/10 ${colorMap[color] || ''}`}>
          <Icon className="w-5 h-5 text-white" />
        </div>
      </div>
      <div className="text-4xl font-black tracking-tight">{value}</div>
    </div>
  );
};

export default StatCard;
