import React, { useState, useEffect } from 'react';
import { ShieldCheck } from 'lucide-react';

const AuditTrail: React.FC = () => {
  const [auditLogs, setAuditLogs] = useState<any[]>([]);

  useEffect(() => {
    fetch('/api/audit')
      .then(res => res.json())
      .then(setAuditLogs)
      .catch(console.error);
  }, []);

  return (
    <div className="glass-panel p-8 rounded-2xl">
      <div className="flex items-center mb-6">
        <ShieldCheck className="w-6 h-6 text-green-400 mr-3" />
        <h3 className="text-xl font-bold">Immutable Enterprise Audit Log</h3>
      </div>
      
      <div className="overflow-x-auto rounded-lg border border-white/10">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/10 text-sm">
              <th className="p-4 font-semibold text-gray-300">Seq</th>
              <th className="p-4 font-semibold text-gray-300">Incident ID</th>
              <th className="p-4 font-semibold text-gray-300">Stage</th>
              <th className="p-4 font-semibold text-gray-300">Actor</th>
              <th className="p-4 font-semibold text-gray-300">Action Detail</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5 font-mono text-sm">
            {auditLogs.length === 0 ? (
              <tr><td colSpan={5} className="p-8 text-center text-gray-500">No audit logs yet. Run the pipeline to generate logs.</td></tr>
            ) : (
              auditLogs.map((log, idx) => (
                <tr key={idx} className="hover:bg-white/5 transition">
                  <td className="p-4 text-gray-400">{log.seq}</td>
                  <td className="p-4 text-uipath-orange">{log.incidentId}</td>
                  <td className="p-4">
                    <span className="px-2 py-1 rounded bg-white/10 text-gray-300 text-xs">{log.stage}</span>
                  </td>
                  <td className="p-4">{log.actor}</td>
                  <td className="p-4 text-gray-400">{log.detail}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default AuditTrail;
