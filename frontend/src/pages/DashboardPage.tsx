import React from 'react';
import HeroSection from '../components/HeroSection';
import AnimatedCards from '../components/AnimatedCards';
import ArchitectureDiagram from '../components/ArchitectureDiagram';
import LiveSimulationTerminal from '../components/LiveSimulationTerminal';
import OrchestratorQueue from '../components/OrchestratorQueue';
import IncidentDashboard from '../components/IncidentDashboard';
import AnalyticsCharts from '../components/AnalyticsCharts';
import AuditTrail from '../components/AuditTrail';
import TeamFooter from '../components/TeamFooter';

const DashboardPage: React.FC = () => {
  return (
    <div className="text-white">
      <HeroSection />
      
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 space-y-32">
        <section id="problem">
          <h2 className="text-4xl font-bold text-center mb-12 bg-clip-text text-transparent bg-gradient-to-r from-uipath-orange to-orange-300">The Problem</h2>
          <AnimatedCards />
        </section>

        <section id="solution" className="text-center py-20 bg-uipath-darker/50 rounded-3xl border border-white/5">
          <h2 className="text-5xl font-extrabold mb-6">Sentinel Solves This</h2>
          <p className="text-2xl text-gray-400 max-w-4xl mx-auto leading-relaxed">
            One BPMN process. <br/>
            <span className="text-uipath-orange font-semibold">AI agents</span> detect anomalies. <br/>
            <span className="text-blue-400 font-semibold">Humans</span> approve. <br/>
            <span className="text-green-400 font-semibold">RPA robots</span> execute. <br/>
            Every decision is fully auditable.
          </p>
        </section>

        <section id="architecture">
          <h2 className="text-4xl font-bold text-center mb-12">Architecture</h2>
          <ArchitectureDiagram />
        </section>

        <section id="demo">
          <h2 className="text-4xl font-bold text-center mb-12">Live Simulation</h2>
          <LiveSimulationTerminal />
        </section>
        
        <section id="queue">
          <h2 className="text-4xl font-bold text-center mb-12">UiPath Orchestrator Integration</h2>
          <OrchestratorQueue />
        </section>

        <section id="incidents">
          <h2 className="text-4xl font-bold text-center mb-12">Incident Dashboard</h2>
          <IncidentDashboard />
        </section>

        <section id="analytics">
          <h2 className="text-4xl font-bold text-center mb-12">Analytics</h2>
          <AnalyticsCharts />
        </section>

        <section id="audit">
          <h2 className="text-4xl font-bold text-center mb-12">Audit Trail</h2>
          <AuditTrail />
        </section>
      </div>

      <TeamFooter />
    </div>
  );
};

export default DashboardPage;
