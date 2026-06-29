import React, { useState, useEffect } from 'react';
import { RefreshCw, Server, Folder, Globe } from 'lucide-react';

const OrchestratorQueue: React.FC = () => {
  const [queueItems, setQueueItems] = useState<any[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isPushing, setIsPushing] = useState(false);

  const fetchQueue = async () => {
    setIsLoading(true);
    try {
      const res = await fetch('/api/queue');
      const data = await res.json();
      setQueueItems(Array.isArray(data) ? data : []);
    } catch (e) {
      console.error(e);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    fetchQueue();
  }, []);

  const pushIncidents = async () => {
    setIsPushing(true);
    try {
      await fetch('/api/pipeline/push', { method: 'POST' });
      await fetchQueue();
    } catch (e) {
      console.error(e);
    }
    setIsPushing(false);
  };

  return (
    <div className="glass-panel p-8 rounded-2xl">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <div className="bg-white/5 p-4 rounded-lg flex items-center border border-white/10">
          <Globe className="w-5 h-5 mr-3 text-blue-400" />
          <div><p className="text-xs text-gray-400">Organization</p><p className="font-semibold">forenly</p></div>
        </div>
        <div className="bg-white/5 p-4 rounded-lg flex items-center border border-white/10">
          <Server className="w-5 h-5 mr-3 text-purple-400" />
          <div><p className="text-xs text-gray-400">Tenant</p><p className="font-semibold">DefaultTenant</p></div>
        </div>
        <div className="bg-white/5 p-4 rounded-lg flex items-center border border-white/10">
          <Folder className="w-5 h-5 mr-3 text-yellow-400" />
          <div><p className="text-xs text-gray-400">Folder</p><p className="font-semibold">Shared</p></div>
        </div>
        <div className="bg-white/5 p-4 rounded-lg flex items-center border border-white/10">
          <div className="w-2 h-2 rounded-full bg-green-500 mr-3 animate-pulse"></div>
          <div><p className="text-xs text-gray-400">Queue</p><p className="font-semibold">IncidentReports</p></div>
        </div>
      </div>

      <div className="flex justify-between items-end mb-4">
        <h3 className="text-2xl font-bold">Latest Queue Items</h3>
        <button 
          onClick={pushIncidents} 
          disabled={isPushing}
          className="flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 mr-2 ${isPushing ? 'animate-spin' : ''}`} />
          {isPushing ? 'Refreshing...' : 'Refresh Queue'}
        </button>
      </div>

      <div className="overflow-x-auto rounded-lg border border-white/10">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/10 text-sm">
              <th className="p-4 font-semibold text-gray-300">Item ID</th>
              <th className="p-4 font-semibold text-gray-300">Reference</th>
              <th className="p-4 font-semibold text-gray-300">Status</th>
              <th className="p-4 font-semibold text-gray-300">Priority</th>
              <th className="p-4 font-semibold text-gray-300">Creation Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {queueItems.length === 0 ? (
               <tr><td colSpan={5} className="p-8 text-center text-gray-500">No items in queue.</td></tr>
            ) : (
              queueItems.map((item, idx) => (
                <tr key={idx} className="hover:bg-white/5 transition">
                  <td className="p-4 font-mono text-sm">{item.Id}</td>
                  <td className="p-4">{item.Reference}</td>
                  <td className="p-4">
                    <span className={`px-2 py-1 rounded text-xs font-semibold ${item.Status === 'New' ? 'bg-blue-500/20 text-blue-300' : item.Status === 'InProgress' ? 'bg-yellow-500/20 text-yellow-300' : 'bg-gray-500/20 text-gray-300'}`}>
                      {item.Status}
                    </span>
                  </td>
                  <td className="p-4">{item.Priority}</td>
                  <td className="p-4 text-sm text-gray-400">{item.CreationTime}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default OrchestratorQueue;
