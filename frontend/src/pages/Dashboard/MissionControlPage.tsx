import { AIDirectorHero } from '../../features/director/components/AIDirectorHero';
import { DigitalTwinCard } from '../../features/leads/components/DigitalTwinCard';
import { MissionWidget } from '../../features/missions/components/MissionWidget';
import { HealthWidget } from '../../features/health/components/HealthWidget';
import { AgentChatFeed } from '../../components/AgentChatFeed';
import { OpportunityMatrix } from '../../components/OpportunityMatrix';
import { SpatialRadarGlobe } from '../../three/RadarGlobe/SpatialRadarGlobe';
import { useWebSocket } from '../../hooks/useWebSocket';

export function MissionControlPage() {
  useWebSocket();

  return (
    <div className="space-y-5 animate-fade-up">
      {/* Page header */}
      <div>
        <h1 className="text-xl font-bold mb-0.5" style={{ color: 'var(--text-primary)' }}>Mission Control</h1>
        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
          AI-recommended actions and live intelligence stream
        </p>
      </div>

      {/* AI Director hero — full width */}
      <AIDirectorHero />

      {/* 3-column grid */}
      <div className="grid grid-cols-12 gap-5">

        {/* Left column: Digital Twin + Mission */}
        <div className="col-span-12 lg:col-span-4 flex flex-col gap-5">
          <DigitalTwinCard />
          <MissionWidget />
        </div>

        {/* Center column: 3D Globe + Agent Feed */}
        <div className="col-span-12 lg:col-span-5 flex flex-col gap-5">
          <div className="surface-card p-5">
            <div className="flex items-center justify-between mb-4">
              <span className="label-accent">Spatial Intelligence Globe</span>
              <span className="badge badge-primary">R3F Live</span>
            </div>
            <SpatialRadarGlobe />
          </div>
          <AgentChatFeed />
        </div>

        {/* Right column: Health + Opportunities */}
        <div className="col-span-12 lg:col-span-3 flex flex-col gap-5">
          <HealthWidget />
          <OpportunityMatrix />
        </div>
      </div>
    </div>
  );
}
