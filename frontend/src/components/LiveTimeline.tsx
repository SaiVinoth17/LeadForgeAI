import React from 'react';
import { useForgeStore } from '../store/useForgeStore';

export function LiveTimeline() {
  const events = useForgeStore((state) => state.timelineEvents);

  return (
    <footer className="glass-card p-4 border border-indigo-500/20">
      <div className="flex justify-between items-center mb-2">
        <span className="text-xs font-bold uppercase tracking-widest text-indigo-400">LIVE BLOOMBERG AUTOMATION TICKER</span>
        <span className="text-[10px] text-emerald-400 font-bold uppercase tracking-wider">● REALTIME STREAM</span>
      </div>

      <div className="flex items-center gap-4 overflow-x-auto pb-1 text-xs">
        {events.map((item, idx) => (
          <div key={idx} className="bg-[#0A0C10] border border-gray-800 rounded-lg px-3.5 py-2 flex items-center gap-2 whitespace-nowrap min-w-[240px]">
            <span className="text-gray-500 text-[10px] font-mono">{item.time}</span>
            <span className="font-bold text-gray-200">{item.action}</span>
            <span className="text-gray-400 text-[11px] truncate">{item.detail}</span>
          </div>
        ))}
      </div>
    </footer>
  );
}
