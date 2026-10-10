import React, { useEffect, useState, useRef } from 'react';
import { AIAssessmentResponse } from './types';
import { FloodMap } from './components/FloodMap';
import { HardwareMonitor } from './components/HardwareMonitor';
import { VolunteerConsole } from './components/VolunteerConsole';
import { 
  Waves, AlertTriangle, ShieldAlert, PhoneCall, CheckCircle2, 
  Globe2, MapPin, Cpu, Activity, Send,
  Volume2, VolumeX, BellRing, Droplets
} from 'lucide-react';

export const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'command' | 'hardware'>('command');
  const [driveMode, setDriveMode] = useState<'hardware' | 'gov_only'>('hardware');
  const [assessment, setAssessment] = useState<AIAssessmentResponse | null>(null);
  const [syncingDHM, setSyncingDHM] = useState<boolean>(false);
  const [lang, setLang] = useState<'ne' | 'en'>('ne');
  const [zoneFilter, setZoneFilter] = useState<string>('ALL');
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);
  const lastAlarmLevelRef = useRef<number>(0);

  const playEmergencySirenAndSpeak = (speechText: string) => {
    if (!soundEnabled) return;
    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      if (AudioCtx) {
        const ctx = new AudioCtx();
        const osc = ctx.createOscillator();
        const gain = ctx.createGain();
        osc.type = 'sawtooth';
        osc.frequency.setValueAtTime(880, ctx.currentTime);
        osc.frequency.setValueAtTime(440, ctx.currentTime + 0.15);
        gain.gain.setValueAtTime(0.2, ctx.currentTime);
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + 0.5);
        osc.connect(gain);
        gain.connect(ctx.destination);
        osc.start();
        osc.stop(ctx.currentTime + 0.5);
      }

      if ('speechSynthesis' in window) {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(speechText);
        utterance.rate = 0.95;
        utterance.lang = lang === 'ne' ? 'ne-NP' : 'en-US';
        window.speechSynthesis.speak(utterance);
      }
    } catch (err) {
      console.error('Audio siren error:', err);
    }
  };

  const scrapeRealDHM = async () => {
    setSyncingDHM(true);
    try {
      const res = await fetch('/api/scraper/sync-dhm', { method: 'POST' });
      if (res.ok) {
        setDriveMode('gov_only');
        await runAIAssessment('gov_only');
      }
    } catch (err) {
      console.error('Scraper error:', err);
    } finally {
      setSyncingDHM(false);
    }
  };

  const runAIAssessment = async (modeOverride?: 'hardware' | 'gov_only') => {
    const activeMode = modeOverride || driveMode;
    try {
      const res = await fetch(`/api/ai/assess?lang=${lang}&drive_mode=${activeMode}`, { method: 'POST' });
      if (res.ok) {
        const data: AIAssessmentResponse = await res.json();
        setAssessment(data);

        const currentLvl = data.forecast?.current_water_level_m ?? 0;
        if (currentLvl >= 5.40 && lastAlarmLevelRef.current < 5.40) {
          const speechMsg = lang === 'ne'
            ? `सावधान! बाढी खतरा स्तर पार भएको छ। राप्ती नदी ${currentLvl} मिटर पुगेको छ।`
            : `Warning! Water level crossed danger threshold. Current stage ${currentLvl} meters.`;
          playEmergencySirenAndSpeak(speechMsg);
        }
        lastAlarmLevelRef.current = currentLvl;
      }
    } catch (err) {
      console.error('Assessment error:', err);
    }
  };

  useEffect(() => {
    runAIAssessment();
    const interval = setInterval(() => {
      runAIAssessment();
    }, 2500);
    return () => clearInterval(interval);
  }, [lang, driveMode]);

  const hw = assessment?.hardware_sensor;
  const forecast = assessment?.forecast;
  const stage = forecast?.current_water_level_m ?? 2.40;
  const dangerDiff = (stage - 5.40).toFixed(2);

  return (
    <div className="min-h-screen bg-stone-100 text-stone-900 font-sans pb-16">
      <header className="bg-white border-b border-stone-200 sticky top-0 z-50 shadow-xs">
        <div className="max-w-7xl mx-auto px-6 py-3.5 flex flex-wrap justify-between items-center gap-4">
          <div className="flex items-center gap-4">
            <div className="w-10 h-10 rounded-md bg-stone-900 text-white flex items-center justify-center font-bold text-lg">
              स
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="text-xl font-bold tracking-tight text-stone-950">SANKET</span>
                <span className="text-xs font-semibold px-2 py-0.5 rounded bg-stone-100 text-stone-600 border border-stone-300">
                  संकेत v0.7
                </span>
                <span className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[11px] font-medium bg-emerald-50 text-emerald-800 border border-emerald-200">
                  <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-pulse"></span>
                  {driveMode === 'hardware' ? 'Arduino Live Fluctuation Active' : 'Gov DHM Scrape Baseline'}
                </span>
              </div>
              <p className="text-xs text-stone-500 font-medium">
                National Early Warning & Household Rescue Command &bull; Rapti Sonari Ward 2, Banke
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2.5">
            <button
              onClick={() => {
                const testMsg = lang === 'ne' 
                  ? 'सावधान! बाढी पूर्वसूचना तथा उद्धार प्रणाली सक्रिय छ।'
                  : 'SANKET early warning siren operational.';
                playEmergencySirenAndSpeak(testMsg);
              }}
              className="inline-flex items-center gap-1.5 px-2.5 py-1.5 bg-red-50 hover:bg-red-100 text-red-700 border border-red-200 rounded text-xs font-semibold shadow-2xs transition"
            >
              <BellRing className="w-3.5 h-3.5" />
              Test Voice Siren
            </button>

            <button
              onClick={() => setSoundEnabled(!soundEnabled)}
              className="p-1.5 bg-white hover:bg-stone-50 border border-stone-300 rounded text-stone-700 shadow-2xs transition"
            >
              {soundEnabled ? <Volume2 className="w-4 h-4 text-emerald-600" /> : <VolumeX className="w-4 h-4 text-stone-400" />}
            </button>

            <div className="flex items-center bg-stone-100 p-1 rounded-md border border-stone-300 text-xs font-medium">
              <button
                onClick={() => setLang('ne')}
                className={`px-3 py-1 rounded transition-colors ${lang === 'ne' ? 'bg-white text-stone-900 shadow-xs font-semibold' : 'text-stone-600'}`}
              >
                नेपाली
              </button>
              <button
                onClick={() => setLang('en')}
                className={`px-3 py-1 rounded transition-colors ${lang === 'en' ? 'bg-white text-stone-900 shadow-xs font-semibold' : 'text-stone-600'}`}
              >
                EN
              </button>
            </div>

            <button
              onClick={scrapeRealDHM}
              disabled={syncingDHM}
              className="inline-flex items-center gap-1.5 px-3 py-2 bg-sky-50 hover:bg-sky-100 border border-sky-300 text-sky-900 rounded-md text-xs font-bold shadow-2xs transition disabled:opacity-50"
            >
              <Globe2 className={`w-3.5 h-3.5 text-sky-600 ${syncingDHM ? 'animate-spin' : ''}`} />
              {syncingDHM ? 'Scraping Gov...' : 'Fetch Real Gov DHM Scrape'}
            </button>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-6 border-t border-stone-100 flex justify-between items-center text-sm font-semibold">
          <div className="flex gap-6">
            <button
              onClick={() => setActiveTab('command')}
              className={`py-2.5 border-b-2 flex items-center gap-2 ${
                activeTab === 'command' ? 'border-stone-900 text-stone-950 font-bold' : 'border-transparent text-stone-500'
              }`}
            >
              <MapPin className="w-4 h-4" />
              Command Center & Rescue Map
            </button>
            <button
              onClick={() => setActiveTab('hardware')}
              className={`py-2.5 border-b-2 flex items-center gap-2 ${
                activeTab === 'hardware' ? 'border-stone-900 text-stone-950 font-bold' : 'border-transparent text-stone-500'
              }`}
            >
              <Cpu className="w-4 h-4" />
              Live Hardware Node (EDGE-UNO-01)
              {hw?.connected && <span className="w-2 h-2 rounded-full bg-emerald-500 inline-block animate-ping" />}
            </button>
          </div>

          <div className="flex items-center gap-2 text-xs py-2">
            <span className="text-stone-500 font-medium">Simulation Driver:</span>
            <button
              onClick={() => setDriveMode(driveMode === 'hardware' ? 'gov_only' : 'hardware')}
              className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded font-bold transition border ${
                driveMode === 'hardware'
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-300'
                  : 'bg-stone-200 text-stone-700 border-stone-300'
              }`}
            >
              <Droplets className="w-3.5 h-3.5 text-emerald-600" />
              {driveMode === 'hardware' ? 'Hardware Probe Submersion (Live)' : 'Static Gov DHM Level'}
            </button>
          </div>
        </div>
      </header>

      <div className="bg-amber-50 border-b border-amber-200 py-2 px-6 text-xs text-amber-900 flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-2 font-medium">
          <Droplets className="w-4 h-4 text-amber-700" />
          <span>
            <b>Hardware-in-the-Loop Mode:</b> Submerge your physical Arduino water probe into a glass of water to dynamically surge the river stage and trigger the AI!
          </span>
        </div>
        <div className="flex items-center gap-4 font-mono font-bold">
          <span>ADC Raw: {hw?.water_raw ?? 0} / 700</span>
          <span>Probe: {hw?.water_level_cm?.toFixed(1) ?? '0.0'} cm</span>
          <span className="text-stone-950 underline font-sans font-semibold">Active River Stage: {stage}m</span>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-6 pt-6 space-y-6">
        {activeTab === 'hardware' ? (
          <HardwareMonitor sensorData={hw} />
        ) : (
          <>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div className="bg-white border border-stone-200 rounded-lg p-4.5 shadow-2xs">
                <div className="flex items-center justify-between text-stone-500 text-[11px] font-semibold uppercase tracking-wider mb-2">
                  <span>River Stage (Kusum #430)</span>
                  <Waves className="w-4 h-4 text-sky-600" />
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-stone-950 tabular-nums">
                    {stage}m
                  </span>
                  <span className={`text-xs font-semibold px-2 py-0.5 rounded border ${
                    stage >= 5.40 ? 'bg-red-50 text-red-700 border-red-200' :
                    stage >= 5.00 ? 'bg-amber-50 text-amber-700 border-amber-200' :
                    'bg-emerald-50 text-emerald-700 border-emerald-200'
                  }`}>
                    {Number(dangerDiff) >= 0 ? `+${dangerDiff}m Above Danger` : `${dangerDiff}m Below Danger`}
                  </span>
                </div>
                <div className="mt-2 pt-2 border-t border-stone-100 flex justify-between text-xs text-stone-600 font-medium">
                  <span>Source: <b>{driveMode === 'hardware' ? 'Arduino Probe' : 'Gov DHM Scrape'}</b></span>
                  <span>Trend: <b>{stage >= 5.0 ? 'Rising 🔴' : 'Safe 🟢'}</b></span>
                </div>
              </div>

              <div className="bg-white border border-stone-200 rounded-lg p-4.5 shadow-2xs">
                <div className="flex items-center justify-between text-stone-500 text-[11px] font-semibold uppercase tracking-wider mb-2">
                  <span>Shelter Network Capacity</span>
                  <ShieldAlert className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-stone-950 tabular-nums">
                    4 Centers
                  </span>
                  <span className="text-xs text-stone-500 font-medium">
                    (970 Person Capacity)
                  </span>
                </div>
                <div className="mt-2 pt-2 border-t border-stone-100 flex justify-between text-xs text-stone-600 font-medium">
                  <span className="text-emerald-700 font-semibold">100% Water & Power Ready</span>
                  <span>Ward: <b>Rapti Sonari-2</b></span>
                </div>
              </div>

              <div className="bg-white border border-stone-200 rounded-lg p-4.5 shadow-2xs">
                <div className="flex items-center justify-between text-stone-500 text-[11px] font-semibold uppercase tracking-wider mb-2">
                  <span>Inundated Homes</span>
                  <AlertTriangle className="w-4 h-4 text-stone-700" />
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-3xl font-extrabold text-stone-950 tabular-nums">
                    {assessment?.inundated_households_count ?? 0}
                  </span>
                  <span className="text-xs text-stone-500 font-medium">
                    of {assessment?.total_households_evaluated ?? 50} homes
                  </span>
                </div>
                <div className="mt-2 pt-2 border-t border-stone-100 flex justify-between text-xs text-stone-600 font-medium">
                  <span className="text-red-600 font-semibold">{assessment?.inundated_households_count ?? 0} Evacuation Targets</span>
                  <span>Physics 2D Model</span>
                </div>
              </div>

              <div className="bg-white border border-stone-200 rounded-lg p-4.5 shadow-2xs">
                <div className="flex items-center justify-between text-stone-500 text-[11px] font-semibold uppercase tracking-wider mb-2">
                  <span>Local SLM Engine</span>
                  <Activity className="w-4 h-4 text-emerald-600" />
                </div>
                <div className="flex items-baseline gap-2">
                  <span className="text-xl font-bold text-stone-900">
                    Phi-3 Mini
                  </span>
                  <span className="text-[11px] font-semibold px-2 py-0.5 rounded bg-stone-100 text-stone-700 border border-stone-200">
                    Offline RAG
                  </span>
                </div>
                <div className="mt-2 pt-2 border-t border-stone-100 flex items-center justify-between text-xs text-stone-600 font-medium">
                  <span className="flex items-center gap-1 text-emerald-700 font-semibold">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Edge Responders Paired
                  </span>
                  <span className="text-stone-500">&lt; 350ms</span>
                </div>
              </div>
            </div>

            <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs">
              <div className="flex flex-wrap items-center justify-between gap-3 mb-4">
                <div>
                  <h2 className="text-base font-bold text-stone-950 flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-stone-700" />
                    Hydraulic Hazard, Multi-Branch River & 4 Evacuation Shelters Map
                  </h2>
                  <p className="text-xs text-stone-500 mt-0.5 font-medium">
                    West Rapti main channel, braided channels, Dudhuwa Khola, and 4 high-ground shelters with dynamic routing
                  </p>
                </div>

                <div className="flex items-center gap-1.5 bg-stone-100 p-1 rounded-md border border-stone-200 text-xs font-medium">
                  {['ALL', 'Kusum Floodplain', 'Kusum Lower', 'Kusum Mid-Ward', 'Agaiya High Ground'].map((zone) => (
                    <button
                      key={zone}
                      onClick={() => setZoneFilter(zone)}
                      className={`px-2.5 py-1 rounded text-[11px] transition ${
                        zoneFilter === zone ? 'bg-white text-stone-950 font-semibold shadow-2xs' : 'text-stone-600'
                      }`}
                    >
                      {zone === 'ALL' ? 'All Settlements' : zone}
                    </button>
                  ))}
                </div>
              </div>

              <FloodMap 
                households={assessment?.evacuation_queue ?? []} 
                selectedZoneFilter={zoneFilter}
              />
            </div>

            <VolunteerConsole dispatches={assessment?.volunteer_dispatches ?? []} />

            <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
              <div className="lg:col-span-7 bg-white border border-stone-200 rounded-lg p-5 shadow-2xs">
                <div className="flex items-center justify-between mb-3 pb-3 border-b border-stone-100">
                  <h3 className="text-sm font-bold text-stone-950 flex items-center gap-2">
                    <AlertTriangle className="w-4 h-4 text-stone-700" />
                    Household Rescue Queue (Named Individuals & Specific Risks)
                  </h3>
                </div>

                <div className="overflow-x-auto">
                  <table className="w-full text-left text-xs">
                    <thead>
                      <tr className="border-b border-stone-200 text-stone-500 uppercase tracking-wider text-[10px] font-bold">
                        <th className="py-2.5 px-2">ID / गृहप्रमुख</th>
                        <th className="py-2.5 px-2">Flood Depth</th>
                        <th className="py-2.5 px-2">जोखिममा रहेका व्यक्ति</th>
                        <th className="py-2.5 px-2">तोकिएको आश्रयस्थल</th>
                        <th className="py-2.5 px-2 text-right">EPI</th>
                      </tr>
                    </thead>
                    <tbody className="divide-y divide-stone-100 text-stone-700">
                      {assessment?.evacuation_queue?.slice(0, 8).map((h, i) => (
                        <tr key={h.household_id} className="hover:bg-stone-50/70 transition-colors">
                          <td className="py-3 px-2">
                            <span className="font-mono font-bold text-stone-900 block">#{i + 1} {h.household_id}</span>
                            <span className="text-stone-950 font-semibold">{h.head_of_household || 'नागरिक'}</span>
                          </td>
                          <td className="py-3 px-2">
                            <span className="font-extrabold text-stone-900 tabular-nums">
                              {h.predicted_water_depth_m}m
                            </span>
                            {h.structural_collapse_threat && (
                              <span className="ml-1.5 inline-block text-[9px] font-bold text-red-700 bg-red-50 border border-red-200 px-1 py-0.2 rounded">
                                COLLAPSE
                              </span>
                            )}
                          </td>
                          <td className="py-3 px-2 text-red-700 font-medium">
                            {h.vulnerability_details || 'सामान्य नागरिक'}
                          </td>
                          <td className="py-3 px-2 text-emerald-800 font-semibold">
                            {h.nearest_shelter}
                          </td>
                          <td className="py-3 px-2 text-right font-mono font-bold text-stone-950 text-sm">
                            {h.evacuation_priority_index}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>

              <div className="lg:col-span-5 bg-white border border-stone-200 rounded-lg p-5 shadow-2xs">
                <div className="flex items-center justify-between mb-3 pb-3 border-b border-stone-100">
                  <h3 className="text-sm font-bold text-stone-950 flex items-center gap-2">
                    <PhoneCall className="w-4 h-4 text-stone-700" />
                    Hyper-Personalized Rescue Alert SMS
                  </h3>
                  <span className="inline-flex items-center gap-1 text-[11px] font-semibold text-emerald-800 bg-emerald-50 border border-emerald-200 px-2 py-0.5 rounded">
                    <Send className="w-3 h-3" /> Dispatched
                  </span>
                </div>

                <div className="space-y-3">
                  {assessment?.queued_alert_payloads?.slice(0, 4).map((alert) => (
                    <div key={alert.household_id} className="bg-stone-50 border border-stone-200 rounded-md p-3.5 space-y-2">
                      <div className="flex items-center justify-between">
                        <span className="font-mono font-bold text-xs text-stone-950">
                          {alert.head_of_household} ({alert.household_id})
                        </span>
                        <span className="text-[10px] font-semibold px-1.5 py-0.5 rounded bg-white text-stone-700 border border-stone-200">
                          {alert.engine}
                        </span>
                      </div>

                      <p className="text-xs text-stone-800 leading-relaxed font-sans bg-white border border-stone-200 rounded p-2.5 shadow-2xs">
                        {alert.sms}
                      </p>

                      <div className="flex items-center justify-between text-[11px] text-stone-500 pt-1 border-t border-stone-100">
                        <span className="font-semibold text-emerald-700">
                          Rescuer: {alert.assigned_rescuer?.name} ({alert.assigned_rescuer?.phone})
                        </span>
                        <span className="font-mono text-stone-600">To: {alert.phone_number}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </>
        )}
      </main>
    </div>
  );
};

export default App;
