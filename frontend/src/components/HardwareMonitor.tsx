import React from 'react';
import { HardwareSensorData } from '../types';
import { Cpu, Droplets, Thermometer, Activity, CheckCircle2, AlertCircle } from 'lucide-react';

interface HardwareMonitorProps {
  sensorData?: HardwareSensorData;
}

export const HardwareMonitor: React.FC<HardwareMonitorProps> = ({ sensorData }) => {
  const isConnected = sensorData?.connected === true && sensorData?.water_raw !== null && sensorData?.water_raw !== undefined;
  const rawWater = sensorData?.water_raw ?? null;
  const waterCm = sensorData?.water_level_cm ?? null;
  const simulatedRiverM = sensorData?.simulated_river_m ?? null;
  const tempC = sensorData?.temperature_c ?? null;
  const humidity = sensorData?.humidity_percent ?? null;

  const probePercent = waterCm !== null ? Math.min(100, Math.round((waterCm / 45.0) * 100)) : 0;

  const bannerClass = isConnected
    ? "border rounded-lg p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4 transition-colors bg-white border-emerald-300"
    : "border rounded-lg p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4 transition-colors bg-red-50/60 border-red-200";

  const iconBoxClass = isConnected
    ? "w-11 h-11 rounded-lg flex items-center justify-center bg-emerald-50 text-emerald-700 border border-emerald-200"
    : "w-11 h-11 rounded-lg flex items-center justify-center bg-red-100 text-red-600 border border-red-200";

  const statusBadgeClass = isConnected
    ? "text-[11px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1 bg-emerald-50 text-emerald-800 border-emerald-200"
    : "text-[11px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1 bg-red-100 text-red-800 border-red-300";

  const probeBarColor = probePercent > 70
    ? "bg-red-600"
    : probePercent > 35
    ? "bg-amber-500"
    : "bg-sky-600";

  return (
    <div className="space-y-6">
      <div className={bannerClass}>
        <div className="flex items-center gap-3.5">
          <div className={iconBoxClass}>
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-stone-950 font-mono">
                {sensorData?.node_id || "EDGE-UNO-01"}
              </h2>
              <span className={statusBadgeClass}>
                {isConnected ? <CheckCircle2 className="w-3 h-3 text-emerald-600" /> : <AlertCircle className="w-3 h-3 text-red-600" />}
                {isConnected ? ("Online (" + (sensorData?.port || "USB") + ")") : "Disconnected (No USB Stream)"}
              </span>
            </div>
            <p className="text-xs text-stone-600 font-medium mt-0.5">
              {isConnected
                ? "Active Physical USB Stream Verified • Water Sensor A0 + DHT11 Pin 2"
                : "Plug in Arduino UNO over USB (115200 baud). Backend is actively scanning ports."}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs text-stone-600 font-medium">
          <div>Baud Rate: <b className="font-mono text-stone-900">115200</b></div>
          <div>Port: <b className="font-mono text-stone-900">{isConnected ? sensorData?.port : "None"}</b></div>
          <div>Stream: <b className={isConnected ? "text-emerald-700 font-semibold" : "text-red-700 font-semibold"}>
            {isConnected ? "Live Active" : "Offline"}
          </b></div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs space-y-3">
          <div className="flex items-center justify-between text-stone-500 text-xs font-semibold uppercase tracking-wider">
            <span>Water Sensor (A0)</span>
            <Droplets className="w-4 h-4 text-sky-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-stone-950 font-mono tabular-nums">
              {isConnected && waterCm !== null ? waterCm.toFixed(1) : "--"}
            </span>
            <span className="text-base font-bold text-stone-500">{isConnected ? "cm" : ""}</span>
          </div>

          <div className="space-y-1.5 pt-1">
            <div className="w-full bg-stone-100 rounded-full h-3 overflow-hidden border border-stone-200">
              <div
                className={"h-full transition-all duration-300 " + probeBarColor}
                style={{ width: (isConnected ? probePercent : 0) + "%" }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-stone-500 font-mono">
              <span>0.0 cm</span>
              <span>{isConnected && rawWater !== null ? ("ADC Raw: " + rawWater + " / 700") : "No Signal"}</span>
              <span>45.0 cm</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs space-y-3">
          <div className="flex items-center justify-between text-stone-500 text-xs font-semibold uppercase tracking-wider">
            <span>Simulated Hydrograph Surge</span>
            <Activity className="w-4 h-4 text-amber-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-stone-950 font-mono tabular-nums">
              {isConnected && simulatedRiverM !== null ? simulatedRiverM.toFixed(2) : "--"}
            </span>
            <span className="text-base font-bold text-stone-500">{isConnected ? "meters" : ""}</span>
          </div>

          <div className="pt-2 border-t border-stone-100 space-y-1 text-xs text-stone-600">
            <div className="flex justify-between">
              <span>Warning Threshold:</span>
              <b className="text-amber-700">5.00m</b>
            </div>
            <div className="flex justify-between">
              <span>Danger Threshold:</span>
              <b className="text-red-700">5.40m</b>
            </div>
          </div>
        </div>

        <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs space-y-3">
          <div className="flex items-center justify-between text-stone-500 text-xs font-semibold uppercase tracking-wider">
            <span>DHT11 Probe (Pin 2)</span>
            <Thermometer className="w-4 h-4 text-emerald-600" />
          </div>

          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="bg-stone-50 border border-stone-200 rounded p-3">
              <span className="text-[11px] text-stone-500 font-medium">Ambient Temp</span>
              <div className="text-2xl font-bold text-stone-900 font-mono tabular-nums mt-0.5">
                {isConnected && tempC !== null ? (tempC.toFixed(1) + "°C") : "--"}
              </div>
            </div>
            <div className="bg-stone-50 border border-stone-200 rounded p-3">
              <span className="text-[11px] text-stone-500 font-medium">Relative Humidity</span>
              <div className="text-2xl font-bold text-stone-900 font-mono tabular-nums mt-0.5">
                {isConnected && humidity !== null ? (humidity.toFixed(1) + "%") : "--"}
              </div>
            </div>
          </div>

          <p className="text-[11px] text-stone-500 font-medium">
            {isConnected ? "Real-time microclimate soil saturation feed." : "Waiting for hardware connection."}
          </p>
        </div>
      </div>
    </div>
  );
};
