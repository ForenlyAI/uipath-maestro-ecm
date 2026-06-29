import React from 'react';
import { motion } from 'framer-motion';

const nodes = [
  { id: '1', label: 'Incident Trigger', color: 'bg-gray-700', border: 'border-gray-500' },
  { id: '2', label: 'IncidentReports Queue', color: 'bg-uipath-orange', border: 'border-orange-500' },
  { id: '3', label: 'Telemetry Analyst (Claude/Gemini)', color: 'bg-purple-900', border: 'border-purple-500' },
  { id: '4', label: 'Risk Assessment', color: 'bg-indigo-900', border: 'border-indigo-500' },
  { id: '5', label: 'Exclusive Gateway', color: 'bg-yellow-900', border: 'border-yellow-500' },
];

const ArchitectureDiagram: React.FC = () => {
  return (
    <div className="flex flex-col items-center justify-center w-full max-w-4xl mx-auto py-12 glass-panel rounded-3xl">
      {nodes.map((node, index) => (
        <React.Fragment key={node.id}>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: index * 0.3 }}
            className={`w-64 py-4 text-center rounded-xl border ${node.color} ${node.border} shadow-lg font-semibold tracking-wide text-white relative z-10`}
          >
            {node.label}
          </motion.div>
          {index < nodes.length - 1 && (
            <motion.div
              initial={{ height: 0, opacity: 0 }}
              whileInView={{ height: 40, opacity: 1 }}
              viewport={{ once: true }}
              transition={{ duration: 0.3, delay: (index * 0.3) + 0.2 }}
              className="w-1 bg-white/20 my-2 relative"
            >
              <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 w-3 h-3 border-r-2 border-b-2 border-white/40 transform rotate-45"></div>
            </motion.div>
          )}
        </React.Fragment>
      ))}

      <div className="flex flex-col md:flex-row w-full justify-center gap-12 mt-8 px-8 relative">
         <motion.div
            initial={{ opacity: 0, y: -20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 1.8 }}
            className="flex flex-col items-center flex-1"
          >
            <div className="text-red-400 font-bold mb-4 bg-red-900/50 px-4 py-1 rounded-full text-sm">If High Risk</div>
            <div className="w-full py-4 text-center rounded-xl border bg-blue-900 border-blue-500 mb-6">Human Review Board</div>
            <div className="w-full py-4 text-center rounded-xl border bg-blue-800 border-blue-400 mb-6">UiPath Action Center</div>
            <div className="w-full py-4 text-center rounded-xl border bg-green-900 border-green-500 mb-6">Approval & RPA Robot</div>
            <div className="w-full py-4 text-center rounded-xl border bg-gray-800 border-gray-600">Audit Log</div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: -20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: 2.1 }}
            className="flex flex-col items-center flex-1"
          >
            <div className="text-green-400 font-bold mb-4 bg-green-900/50 px-4 py-1 rounded-full text-sm">If Low Risk</div>
            <div className="w-full py-4 text-center rounded-xl border bg-teal-900 border-teal-500 mb-6">Fast Track</div>
            <div className="w-full py-4 text-center rounded-xl border bg-teal-800 border-teal-400 mb-6">Autonomous Remediation</div>
            <div className="w-full py-4 text-center rounded-xl border bg-gray-800 border-gray-600">Audit Log</div>
          </motion.div>
      </div>
    </div>
  );
};

export default ArchitectureDiagram;
