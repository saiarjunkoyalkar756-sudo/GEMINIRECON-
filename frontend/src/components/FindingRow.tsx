import React, { useState } from 'react';
import { AlertTriangle, ChevronRight } from 'lucide-react';

const FindingRow = ({ finding }: any) => {
  const [expanded, setExpanded] = useState(false);
  
  const severityStyles = {
    CRITICAL: { text: 'text-red-400', bg: 'bg-red-500/15', border: 'border-red-500' },
    HIGH: { text: 'text-orange-400', bg: 'bg-orange-500/15', border: 'border-orange-500' },
    MEDIUM: { text: 'text-yellow-400', bg: 'bg-yellow-500/15', border: 'border-yellow-500' },
    LOW: { text: 'text-green-400', bg: 'bg-green-500/15', border: 'border-green-500' },
  };

  const styles = severityStyles[finding.severity] || severityStyles.LOW;

  return (
    <div className={`p-4 rounded-xl mb-3 last:mb-0 transition-all duration-300 ${styles.border} ${styles.bg} hover:shadow-xl hover:shadow-${styles.text.split('-')[2]}-500/20`}>
      <div className="flex justify-between items-center cursor-pointer" onClick={() => setExpanded(!expanded)}>
        <div className="flex items-center gap-2 w-full">
          <span className={`text-xs font-bold uppercase px-2 py-1 rounded ${styles.text}`}>
            {finding.severity}
          </span>
          <span className="font-medium flex-1">{finding.title}</span>
          <ChevronRight className={`w-4 h-4 transition-transform ${expanded ? 'rotate-90' : ''}`} />
        </div>
      </div>
      {expanded && (
        <div className="mt-3 p-3 bg-black/50 rounded-md text-xs border border-gray-700">
          <p><span className="font-bold text-gray-400">Asset:</span> {finding.asset}</p>
          <p><span className="font-bold text-gray-400">URL:</span> {finding.url || 'N/A'}</p>
          <p className="mt-2 text-gray-300">Remediation: This finding requires immediate attention. Update software, sanitize inputs, and implement robust security controls.</p>
        </div>
      )}
    </div>
  );
};

export default FindingRow;
