import React from 'react';
import { motion } from 'framer-motion';
import { Play, GitBranch, Activity, ShieldCheck, Cpu } from 'lucide-react';

const HeroSection: React.FC = () => {
  return (
    <div className="relative overflow-hidden bg-uipath-darker py-24 sm:py-32 border-b border-white/10">
      <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-5"></div>
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-full bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-uipath-orange/20 via-uipath-dark to-uipath-dark pointer-events-none"></div>

      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.8 }}
        >
          <p className="text-uipath-orange font-semibold tracking-wide uppercase text-sm mb-4">
            🏆 UiPath AgentHack — Track 2: UiPath Maestro BPMN
          </p>
          <h1 className="text-6xl md:text-8xl font-extrabold tracking-tight text-white mb-6">
            ⚡ SENTINEL
          </h1>
          <p className="text-2xl text-gray-300 font-medium mb-8">
            Agentic Cloud-GPU Orchestrator
          </p>
          
          <div className="max-w-3xl mx-auto text-lg text-gray-400 space-y-2 mb-12">
            <p>An autonomous humanoid RL training fleet manager built end-to-end on UiPath Maestro BPMN.</p>
            <p>
              <span className="text-uipath-orange">AI agents analyze anomalies.</span>{' '}
              <span className="text-blue-400">Humans approve critical gates.</span>{' '}
              <span className="text-green-400">RPA robots execute.</span>
            </p>
            <p className="font-semibold text-white/80">Everything is governed through BPMN.</p>
          </div>

          <div className="flex flex-wrap justify-center gap-6 mb-16">
            <a href="#demo" className="flex items-center px-8 py-4 bg-uipath-orange text-white rounded-full font-bold text-lg hover:bg-orange-600 transition shadow-[0_0_20px_rgba(250,70,22,0.4)]">
              <Play className="w-5 h-5 mr-2" fill="currentColor" />
              Run Live Demo
            </a>
            <a href="https://github.com/swatiicfai/uipath-maestro-ecm" target="_blank" rel="noreferrer" className="flex items-center px-8 py-4 bg-white/10 text-white rounded-full font-bold text-lg hover:bg-white/20 transition border border-white/20">
              <GitBranch className="w-5 h-5 mr-2" />
              View on GitHub
            </a>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 max-w-4xl mx-auto mt-12 border-t border-white/10 pt-12">
            {[
              { label: 'BPMN Process Containers', value: '8', icon: Activity },
              { label: 'AI Agents', value: '3', icon: Cpu },
              { label: 'BPMN Swimlane Roles', value: '9', icon: ShieldCheck },
              { label: 'Grand Prize Pool', value: '$48K', icon: null },
            ].map((stat, i) => (
              <div key={i} className="flex flex-col items-center">
                {stat.icon && <stat.icon className="w-8 h-8 text-uipath-orange mb-3 opacity-80" />}
                <span className="text-3xl font-bold text-white mb-1">{stat.value}</span>
                <span className="text-sm text-gray-400 text-center uppercase tracking-wider">{stat.label}</span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
};

export default HeroSection;
