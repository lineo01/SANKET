import React, { useEffect, useState } from 'react';
import { HealthStatus, Household, RiverReading } from './types';
import { Database, Waves, Home, AlertCircle, RefreshCw } from 'lucide-react';
export const App: React.FC = () => {
  const [health, setHealth] = useState<HealthStatus | null>(null);
  const [households, setHouseholds] = useState<Household[]>([]);
  const [riverReadings, setRiverReadings] = useState<RiverReading[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [seeding, setSeeding] = useState<boolean>(false);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [hRes, hhRes, rRes] = await Promise.all([
        fetch('/api/health'),
        fetch('/api/households?limit=10'),
        fetch('/api/river/readings?limit=5'),
      ]);

      if (hRes.ok) setHealth(await hRes.json());
      if (hhRes.ok) setHouseholds(await hhRes.json());
      if (rRes.ok) setRiverReadings(await rRes.json());
    } catch (err) {
      console.error('Backend connection error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSeed = async () => {
    setSeeding(true);
    try {
      const res = await fetch('/api/data/seed', { method: 'POST' });
      if (res.ok) {
        await fetchData();
      }
    } catch (err) {
      console.error('Seed error:', err);
    } finally {
      setSeeding(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 p-6 text-slate-100 font-sans">
      <header className="max-w-6xl mx-auto border-b border-slate-800 pb-5 mb-8 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-extrabold tracking-tight text-cyan-400">
            SANKET <span className="text-sm font-semibold text-slate-400">संकेत</span>
          </h1>
          <p className="text-sm text-slate-400">
            Offline-First AI Flood Early-Warning & Household-Alert System (Phase 1: Foundation)
          </p>
        </div>
        <button
          onClick={handleSeed}
          disabled={seeding}
          className="flex items-center gap-2 px-4 py-2 bg-cyan-600 hover:bg-cyan-500 disabled:opacity-50 text-white rounded-md text-sm font-medium transition"
        >
          <RefreshCw className={`w-4 h-4 ${seeding ? 'animate-spin' : ''}`} />
          {seeding ? 'Seeding Data...' : 'Seed Database'}
        </button>
      </header>

      <main className="max-w-6xl mx-auto space-y-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
              <Database className="w-4 h-4 text-emerald-400" /> System Status
            </div>
            <div className="text-2xl font-bold text-emerald-400">
              {health ? health.status.toUpperCase() : 'OFFLINE'}
            </div>
            <div className="text-xs text-slate-500 mt-1">DB: {health?.database || 'none'}</div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
              <Home className="w-4 h-4 text-cyan-400" /> Households Loaded
            </div>
            <div className="text-2xl font-bold">{health?.household_count ?? 0}</div>
            <div className="text-xs text-slate-500 mt-1">Target Ward: Rapti Sonari-2</div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
              <Waves className="w-4 h-4 text-blue-400" /> River Readings
            </div>
            <div className="text-2xl font-bold">{health?.river_readings_count ?? 0}</div>
            <div className="text-xs text-slate-500 mt-1">DHM Kusum Station #430</div>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <div className="flex items-center gap-2 text-slate-400 text-sm mb-1">
              <AlertCircle className="w-4 h-4 text-amber-400" /> Edge Sensors
            </div>
            <div className="text-2xl font-bold">{health?.sensor_readings_count ?? 0}</div>
            <div className="text-xs text-slate-500 mt-1">LoRa Mesh Nodes</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h2 className="text-lg font-semibold text-slate-200 mb-3">Households Schema Test (Top 5)</h2>
            {loading ? (
              <p className="text-sm text-slate-400">Loading households...</p>
            ) : households.length === 0 ? (
              <p className="text-sm text-slate-500">No data. Click "Seed Database" above.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-800 text-slate-300">
                    <tr>
                      <th className="p-2">ID</th>
                      <th className="p-2">Zone</th>
                      <th className="p-2">Elev (m)</th>
                      <th className="p-2">Dist (m)</th>
                      <th className="p-2">Vuln (E/C/D)</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-400">
                    {households.slice(0, 5).map((h) => (
                      <tr key={h.household_id}>
                        <td className="p-2 font-mono text-cyan-400">{h.household_id}</td>
                        <td className="p-2">{h.zone}</td>
                        <td className="p-2">{h.elevation_m}m</td>
                        <td className="p-2">{h.distance_to_river_m}m</td>
                        <td className="p-2">{h.elderly}/{h.children}/{h.disabled}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-lg p-5">
            <h2 className="text-lg font-semibold text-slate-200 mb-3">River Levels (DHM Feed Test)</h2>
            {loading ? (
              <p className="text-sm text-slate-400">Loading river telemetry...</p>
            ) : riverReadings.length === 0 ? (
              <p className="text-sm text-slate-500">No telemetry. Click "Seed Database" above.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-800 text-slate-300">
                    <tr>
                      <th className="p-2">Station</th>
                      <th className="p-2">Level</th>
                      <th className="p-2">Warning</th>
                      <th className="p-2">Danger</th>
                      <th className="p-2">Trend</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-800 text-slate-400">
                    {riverReadings.map((r, i) => (
                      <tr key={i}>
                        <td className="p-2 font-mono text-blue-400">{r.station_name}</td>
                        <td className="p-2 font-bold text-slate-200">{r.water_level_m}m</td>
                        <td className="p-2 text-amber-400">{r.warning_level_m}m</td>
                        <td className="p-2 text-rose-400">{r.danger_level_m}m</td>
                        <td className="p-2 capitalize">{r.trend}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      </main>
    </div>
  );
};

export default App;