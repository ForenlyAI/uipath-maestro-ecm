import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, ChevronDown, ChevronRight, X } from 'lucide-react';

const IncidentDashboard: React.FC = () => {
  const [incidents, setIncidents] = useState<any[]>([]);
  const [selectedIncident, setSelectedIncident] = useState<any | null>(null);

  useEffect(() => {
    fetch('/api/incidents')
      .then(res => res.json())
      .then(data => setIncidents(data))
      .catch(console.error);
  }, []);

  return (
    <div className="glass-panel p-8 rounded-2xl relative">
      <div className="flex justify-between items-center mb-6">
        <div className="relative">
          <Search className="w-5 h-5 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input 
            type="text" 
            placeholder="Search incidents..." 
            className="bg-white/5 border border-white/10 rounded-lg pl-10 pr-4 py-2 text-white focus:outline-none focus:border-uipath-orange transition w-64"
          />
        </div>
        <div className="flex gap-2">
          <button className="bg-white/5 border border-white/10 px-4 py-2 rounded-lg text-sm hover:bg-white/10 transition flex items-center">
            Filter <ChevronDown className="w-4 h-4 ml-2" />
          </button>
        </div>
      </div>

      <div className="overflow-x-auto rounded-lg border border-white/10">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-white/10 text-sm">
              <th className="p-4 font-semibold text-gray-300">Incident ID</th>
              <th className="p-4 font-semibold text-gray-300">Category</th>
              <th className="p-4 font-semibold text-gray-300">Severity</th>
              <th className="p-4 font-semibold text-gray-300">Action</th>
              <th className="p-4"></th>
            </tr>
          </thead>
          <tbody className="divide-y divide-white/5">
            {incidents.map((incident, idx) => (
              <tr key={idx} className="hover:bg-white/5 transition cursor-pointer" onClick={() => setSelectedIncident(incident)}>
                <td className="p-4 font-mono text-sm text-uipath-orange">{incident.incidentId}</td>
                <td className="p-4">{incident.category}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-semibold ${incident.severity === 'CRITICAL' ? 'bg-red-500/20 text-red-300' : incident.severity === 'HIGH' ? 'bg-orange-500/20 text-orange-300' : 'bg-yellow-500/20 text-yellow-300'}`}>
                    {incident.severity}
                  </span>
                </td>
                <td className="p-4 text-sm text-gray-400">{incident.subject}</td>
                <td className="p-4 text-right"><ChevronRight className="w-5 h-5 text-gray-500 inline" /></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <AnimatePresence>
        {selectedIncident && (
          <motion.div
            initial={{ opacity: 0, x: 50 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: 50 }}
            className="fixed top-0 right-0 h-full w-[500px] bg-uipath-darker border-l border-white/10 shadow-2xl p-8 overflow-y-auto z-50"
          >
            <button onClick={() => setSelectedIncident(null)} className="absolute top-6 right-6 text-gray-400 hover:text-white transition">
              <X className="w-6 h-6" />
            </button>
            <h2 className="text-2xl font-bold mb-2">Incident Details</h2>
            <p className="font-mono text-uipath-orange mb-8">{selectedIncident.incidentId}</p>

            <div className="space-y-6">
              <div>
                <h4 className="text-sm text-gray-400 uppercase tracking-wide mb-1">Subject</h4>
                <p className="text-lg">{selectedIncident.subject}</p>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-white/5 p-4 rounded-lg">
                  <h4 className="text-xs text-gray-400 uppercase mb-1">Severity</h4>
                  <p className="font-bold text-red-400">{selectedIncident.severity}</p>
                </div>
                <div className="bg-white/5 p-4 rounded-lg">
                  <h4 className="text-xs text-gray-400 uppercase mb-1">Category</h4>
                  <p className="font-bold">{selectedIncident.category}</p>
                </div>
              </div>

              <div>
                <h4 className="text-sm text-gray-400 uppercase tracking-wide mb-2">Metrics</h4>
                <pre className="bg-black/50 p-4 rounded-lg text-xs text-gray-300 overflow-x-auto border border-white/5">
                  {JSON.stringify(selectedIncident.metrics || selectedIncident, null, 2)}
                </pre>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default IncidentDashboard;
