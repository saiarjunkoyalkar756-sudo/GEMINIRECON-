import React from 'react';
import { Globe, ExternalLink } from 'lucide-react';

const AssetRow = ({ asset }: any) => (
  <tr className="border-b border-gray-800 hover:bg-white/5 transition-colors group">
    <td className="py-3 px-4">
      <div className="flex items-center gap-3">
        <div className="p-2 rounded-lg bg-blue-500/10 text-blue-400">
          <Globe className="w-4 h-4" />
        </div>
        <span className="font-medium">{asset.domain}</span>
      </div>
    </td>
    <td className="py-3 px-4 text-gray-400">{asset.ip || 'N/A'}</td>
    <td className="py-4 px-4">
      <div className="flex gap-2 flex-wrap">
        {asset.tech && asset.tech.map((t: string, i: number) => (
          <span key={i} className="px-2 py-1 rounded-md bg-cyan-500/10 text-cyan-400 text-[10px] font-bold uppercase">
            {t}
          </span>
        ))}
      </div>
    </td>
    <td className="py-4 px-4">
      <span className={`px-2 py-1 rounded-full text-[10px] font-bold uppercase ${
        asset.status === 'LIVE' ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
      }`}>
        {asset.status || 'Unknown'}
      </span>
    </td>
    <td className="py-4 px-4 text-right">
      <ExternalLink className="w-4 h-4 text-gray-500 hover:text-cyan-400 transition-colors" />
    </td>
  </tr>
);

export default AssetRow;
