import React, { useState, useEffect, useRef } from 'react';
import { Terminal, Play } from 'lucide-react';

const LINE_DELAY_MS = 350;

// ---------------------------------------------------------------------------
// Offline fallback — mirrors the hardcoded data in sentinel.js so the demo
// works without the FastAPI backend running.
// ---------------------------------------------------------------------------
const OFFLINE_INCIDENTS = [
  {
    id: 'IR-20260607-0003',
    title: 'HARDWARE_FAULT: GPU thermal throttling detected on training node',
    analyst: 'HARDWARE_FAULT risk=0.45 conf=0.92 action=HOLD',
    gateway: 'HITL',
    cloud: 'provider aws-us-east-1 (AWS Spot (us-east-1, H100)) tier=A openIssues=2',
    action: 'QA-00004 (OPEN, owner=review-board)',
  },
  {
    id: 'IR-20260607-0001',
    title: 'GRADIENT_COLLAPSE: reward flatlined and gradients vanished at step 24000',
    analyst: 'GRADIENT_COLLAPSE risk=0.45 conf=0.92 action=RESTART',
    gateway: 'HITL',
    cloud: 'provider aws-us-east-1 (AWS Spot (us-east-1, H100)) tier=A openIssues=2',
    action: 'QA-00005 (OPEN, owner=review-board)',
  },
  {
    id: 'IR-20260607-0004',
    title: 'Idle GPU spend: instance kept running 40 min after the run finished',
    analyst: 'RESOURCE_RISK risk=0.05 conf=0.92 action=PROCEED',
    gateway: 'FAST',
    cloud: 'provider gcp-us-central1 (GCP (us-central1, A100/L4)) tier=B openIssues=1',
    action: 'QA-00006 (OPEN, owner=auto-remediation)',
  },
  {
    id: 'IR-20260607-0002',
    title: 'LOSS_DIVERGENCE: critic loss diverging and reward crashing on a bipedal run',
    analyst: 'LOSS_DIVERGENCE risk=0.45 conf=0.92 action=RESTART',
    gateway: 'HITL',
    cloud: 'provider amd-devcloud (AMD Developer Cloud (MI300X)) tier=A openIssues=0',
    action: 'QA-00007 (OPEN, owner=review-board)',
  },
  {
    id: 'IR-20260607-0005',
    title: 'Cloud GPU quota nearly exhausted on the training project',
    analyst: 'RESOURCE_RISK risk=0.15 conf=0.92 action=PROCEED',
    gateway: 'HITL',
    cloud: 'provider aws-us-east-1 (AWS Spot (us-east-1, H100)) tier=A openIssues=2',
    action: 'QA-00008 (OPEN, owner=review-board)',
  },
  {
    id: 'IR-20260607-0006',
    title: 'Idle GPU spend: second instance left running 55 min post-completion',
    analyst: 'RESOURCE_RISK risk=0.03 conf=0.95 action=PROCEED',
    gateway: 'FAST',
    cloud: 'provider gcp-us-central1 (GCP (us-central1, A100/L4)) tier=B openIssues=0',
    action: 'QA-00009 (OPEN, owner=auto-remediation)',
  },
  {
    id: 'IR-20260607-0007',
    title: 'HARDWARE_FAULT: NVLink error rate spiking on multi-GPU node',
    analyst: 'HARDWARE_FAULT risk=0.55 conf=0.89 action=HOLD',
    gateway: 'HITL',
    cloud: 'provider aws-us-east-1 (AWS Spot (us-east-1, H100)) tier=A openIssues=3',
    action: 'QA-00010 (OPEN, owner=review-board)',
  },
  {
    id: 'IR-20260607-0008',
    title: 'GRADIENT_COLLAPSE: policy gradient norm collapsed on grasping skill run',
    analyst: 'GRADIENT_COLLAPSE risk=0.50 conf=0.91 action=RESTART',
    gateway: 'HITL',
    cloud: 'provider amd-devcloud (AMD Developer Cloud (MI300X)) tier=A openIssues=1',
    action: 'QA-00011 (OPEN, owner=review-board)',
  },
];

function buildOfflineLines(): string[] {
  const lines: string[] = [
    'Sentinel — Agentic Cloud-GPU Orchestrator',
    'Connecting to UiPath Orchestrator Queue: IncidentReports...',
    '✓ Queue connected. Fetching incidents...',
    `✓ ${OFFLINE_INCIDENTS.length} anomaly events dequeued.`,
    '━'.repeat(56),
  ];

  let hitl = 0;
  let auto = 0;

  for (const inc of OFFLINE_INCIDENTS) {
    lines.push('');
    lines.push(`=== ${inc.id} :: ${inc.title}`);
    lines.push(`  analyst [offline:rules] -> ${inc.analyst}`);
    if (inc.gateway === 'HITL') {
      lines.push('  gateway -> HITL: routed to Researcher Review Board (Action Center)');
      hitl++;
    } else {
      lines.push('  gateway -> FAST TRACK: autonomous remediation, no human gate');
      auto++;
    }
    lines.push(`  cloud   -> ${inc.cloud}`);
    lines.push(`  action  -> ${inc.action}`);
  }

  lines.push('');
  lines.push('━'.repeat(56));
  lines.push(
    `--- processed ${OFFLINE_INCIDENTS.length} anomaly event(s): ${hitl} routed to HITL, ${auto} autonomous fast-track ---`,
  );
  lines.push('✓ All transactions marked Successful in Orchestrator Queue.');
  lines.push('✅ Audit log written. Pipeline complete.');
  return lines;
}

// ---------------------------------------------------------------------------

const LiveSimulationTerminal: React.FC = () => {
  const [logs, setLogs] = useState<string[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const endRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    endRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [logs]);

  const animateLines = async (lines: string[]) => {
    for (let i = 0; i < lines.length; i++) {
      await new Promise<void>(resolve => setTimeout(resolve, LINE_DELAY_MS));
      setLogs(prev => [...prev, lines[i]]);
    }
  };

  const runPipeline = async () => {
    if (isRunning) return;
    setIsRunning(true);
    setLogs(['sentinel@uipath-maestro-ecm:~$ python run_pipeline.py', '']);

    try {
      // Try the live API first (works when FastAPI backend is running).
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 5000);

      const response = await fetch('/api/pipeline/run', { signal: controller.signal });
      clearTimeout(timeout);

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`);
      }
      const data = await response.json();
      const lines: string[] = data.lines ?? [];
      await animateLines(lines);
      await new Promise<void>(resolve => setTimeout(resolve, LINE_DELAY_MS));
      setLogs(prev => [...prev, '', '✅ Pipeline complete.']);
    } catch {
      // Backend not reachable — run the fully offline simulation instead.
      setLogs(['sentinel@uipath-maestro-ecm:~$ python run_pipeline.py', '']);
      await animateLines(buildOfflineLines());
    } finally {
      setIsRunning(false);
    }
  };

  const getLineClass = (log: string) => {
    if (log.startsWith('sentinel@')) return 'text-green-400 font-bold';
    if (log.includes('ERROR') || log.includes('Error')) return 'text-red-400';
    if (log.includes('WARNING') || log.includes('FAST TRACK')) return 'text-yellow-300';
    if (log.includes('HITL') || log.includes('review-board')) return 'text-blue-300';
    if (log.includes('===')) return 'text-orange-400 font-semibold mt-2';
    if (log.includes('✅') || log.startsWith('✓')) return 'text-green-400 font-bold mt-2';
    if (log.includes('processed')) return 'text-purple-300 font-semibold mt-2';
    if (log.includes('analyst')) return 'text-cyan-300';
    if (log.includes('cloud')) return 'text-sky-300';
    if (log.includes('action')) return 'text-indigo-300';
    if (log.startsWith('━')) return 'text-gray-600';
    if (log.startsWith('Sentinel') || log.startsWith('Connecting') || log.startsWith('✓ Queue') || log.startsWith('✓ ')) return 'text-emerald-400';
    return 'text-gray-300';
  };

  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-xl font-semibold flex items-center">
          <Terminal className="mr-2" /> Watch Sentinel in Action
        </h3>
        <button
          onClick={runPipeline}
          disabled={isRunning}
          className={`flex items-center px-6 py-2 rounded-lg font-bold transition ${
            isRunning ? 'bg-gray-600 cursor-not-allowed' : 'bg-uipath-orange hover:bg-orange-600'
          }`}
        >
          <Play className="w-4 h-4 mr-2" />
          {isRunning ? 'Running...' : 'Run Pipeline Simulation'}
        </button>
      </div>

      <div className="bg-[#0c0c0c] rounded-xl border border-gray-700 shadow-2xl overflow-hidden font-mono text-sm h-96 flex flex-col">
        <div className="bg-gray-800 px-4 py-2 flex gap-2 items-center border-b border-gray-700">
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
          <div className="w-3 h-3 rounded-full bg-yellow-500"></div>
          <div className="w-3 h-3 rounded-full bg-green-500"></div>
          <span className="ml-2 text-gray-400 text-xs">Terminal — sentinel</span>
        </div>
        <div className="p-4 overflow-y-auto flex-1 text-gray-300 space-y-0.5">
          {logs.length === 0 && (
            <div className="text-gray-600">$ Waiting for pipeline to start...</div>
          )}
          {logs.map((log, i) => (
            <div key={i} className={`leading-relaxed ${getLineClass(log)}`}>
              {log || '\u00A0'}
            </div>
          ))}
          {isRunning && <div className="animate-pulse text-green-400 inline-block">▋</div>}
          <div ref={endRef} />
        </div>
      </div>
    </div>
  );
};

export default LiveSimulationTerminal;
