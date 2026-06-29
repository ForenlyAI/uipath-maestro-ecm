import React from 'react';

const TeamFooter: React.FC = () => {
  return (
    <footer className="bg-uipath-darker border-t border-white/10 pt-20 pb-10 mt-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="text-3xl font-bold mb-2">Built by Forenly AI</h2>
          <p className="text-uipath-orange tracking-widest uppercase text-sm font-semibold">UiPath AgentHack 2026</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-4 gap-8 mb-16">
          <div>
            <h3 className="font-bold text-lg mb-1">Diya Majee</h3>
            <p className="text-sm text-gray-400 mb-3">Lead Architect & UiPath Maestro</p>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-1">Swati Gupta</h3>
            <p className="text-sm text-gray-400 mb-3">AI Agent Integration & Queue Consumer</p>
            <ul className="text-xs text-gray-500 space-y-1">
              <li>• Claude/Gemini Integration</li>
              <li>• Queue Consumer</li>
              <li>• CRM Integration</li>
              <li>• Testing</li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-1">Dundu Lawan</h3>
            <p className="text-sm text-gray-400 mb-3">AI Integration & Platform Engineer</p>
            <ul className="text-xs text-gray-500 space-y-1">
              <li>• UiPath Orchestrator Integration</li>
              <li>• OAuth 2.0 Cloud Authentication</li>
              <li>• Live Queue Integration</li>
              <li>• Environment & Cloud Configuration</li>
              <li>• End-to-End Integration Testing</li>
              <li>• Production Deployment Validation</li>
              <li>• Enterprise Dashboard Development</li>
            </ul>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-1">Soujanya</h3>
            <p className="text-sm text-gray-400 mb-3">Devpost & Architecture Documentation</p>
          </div>
        </div>

        <div className="border-t border-white/10 pt-8 flex flex-col md:flex-row justify-between items-center text-sm text-gray-500">
          <div className="flex items-center space-x-2 mb-4 md:mb-0">
            <span className="text-white font-bold text-lg tracking-tight">⚡ SENTINEL</span>
            <span>|</span>
            <span>Agentic Cloud-GPU Orchestrator</span>
          </div>
          <div className="flex space-x-6">
            <a href="https://github.com/swatiicfai/uipath-maestro-ecm" className="hover:text-uipath-orange transition">GitHub</a>
            <a href="#" className="hover:text-uipath-orange transition">Devpost</a>
            <a href="#" className="hover:text-uipath-orange transition">Discord</a>
            <span>Apache 2.0 License</span>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default TeamFooter;
