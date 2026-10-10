import React from 'react';
import { HardwareSensorData } from '../types';
import { Cpu, Droplets, Thermometer, Activity, CheckCircle2, AlertCircle } from 'lucide-react';

interface HardwareMonitorProps {
  sensorData?: HardwareSensorData;
}

export const HardwareMonitor: React.FC<HardwareMonitorProps> = ({ sensorData }) => {
  const isConnected = sensorData?.connected ?? false;
  const rawWater = sensorData?.water_raw ?? 0;
  const waterCm = sensorData?.water_level_cm ?? 0;
  const simulatedRiverM = sensorData?.simulated_river_m ?? 2.4;
  const tempC = sensorData?.temperature_c ?? 26.5;
  const humidity = sensorData?.humidity_percent ?? 82.0;

  const probePercent = Math.min(100, Math.round((waterCm / 45.0) * 100));

  return (
    <div className="space-y-6">
      <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3.5">
          <div className={`w-11 h-11 rounded-lg flex items-center justify-center ${
            isConnected ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-stone-100 text-stone-500 border border-stone-200'
          }`}>
            <Cpu className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-base font-bold text-stone-950 font-mono">
                {sensorData?.node_id ?? 'EDGE-UNO-01'}
              </h2>
              <span className={`text-[11px] font-semibold px-2 py-0.5 rounded-full border flex items-center gap-1 ${
                isConnected
                  ? 'bg-emerald-50 text-emerald-800 border-emerald-200'
                  : 'bg-amber-50 text-amber-800 border-amber-200'
              }`}>
                {isConnected ? <CheckCircle2 className="w-3 h-3 text-emerald-600" /> : <AlertCircle className="w-3 h-3 text-amber-600" />}
                {isConnected ? `Online (${sensorData?.port ?? 'USB Serial'})` : 'Polling Auto-Detect'}
              </span>
            </div>
            <p className="text-xs text-stone-500 font-medium mt-0.5">
              Micro-Culvert Edge Hydrology Station &bull; Analog Water Sensor (A0) + DHT11 Environmental Probe (Pin 2)
            </p>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs text-stone-600 font-medium">
          <div>Baud Rate: <b className="font-mono text-stone-900">115200</b></div>
          <div>Sample Frequency: <b className="font-mono text-stone-900">1.0 Hz (1000ms)</b></div>
          <div>Telemetry Status: <b className="text-emerald-700 font-semibold">Active Streaming</b></div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs space-y-3">
          <div className="flex items-center justify-between text-stone-500 text-xs font-semibold uppercase tracking-wider">
            <span>Culvert Water Column Depth</span>
            <Droplets className="w-4 h-4 text-sky-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-stone-950 font-mono tabular-nums">
              {waterCm.toFixed(1)}
            </span>
            <span className="text-base font-bold text-stone-500">cm</span>
          </div>
          <div className="space-y-1.5 pt-1">
            <div className="w-full bg-stone-100 rounded-full h-3 overflow-hidden border border-stone-200">
              <div
                className={`h-full transition-all duration-500 ${
                  probePercent > 70 ? 'bg-red-600' : probePercent > 35 ? 'bg-amber-500' : 'bg-sky-600'
                }`}
                style={{ width: `${probePercent}%` }}
              />
            </div>
            <div className="flex justify-between text-[11px] text-stone-500 font-mono">
              <span>0.0 cm</span>
              <span>ADC Raw: {rawWater} / 700</span>
              <span>45.0 cm</span>
            </div>
          </div>
        </div>

        <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs space-y-3">
          <div className="flex items-center justify-between text-stone-500 text-xs font-semibold uppercase tracking-wider">
            <span>Simulated Hydrograph Translation</span>
            <Activity className="w-4 h-4 text-amber-600" />
          </div>
          <div className="flex items-baseline gap-2">
            <span className="text-4xl font-extrabold text-stone-950 font-mono tabular-nums">
              {simulatedRiverM.toFixed(2)}
            </span>
            <span className="text-base font-bold text-stone-500">meters</span>
          </div>
          <div className="pt-2 border-t border-stone-100 space-y-1 text-xs text-stone-600">
            <div className="flex justify-between">
              <span>DHM Warning Level:</span>
              <b className="text-amber-700">5.00m</b>
            </div>
            <div className="flex justify-between">
              <span>DHM Danger Level:</span>
              <b className="text-red-700">5.40m</b>
            </div>
          </div>
        </div>

        <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs space-y-3">
          <div className="flex items-center justify-between text-stone-500 text-xs font-semibold uppercase tracking-wider">
            <span>DHT11 Micro-Climate</span>
            <Thermometer className="w-4 h-4 text-emerald-600" />
          </div>
          <div className="grid grid-cols-2 gap-3 pt-1">
            <div className="bg-stone-50 border border-stone-200 rounded p-3">
              <span className="text-[11px] text-stone-500 font-medium">Ambient Temp</span>
              <div className="text-2xl font-bold text-stone-900 font-mono tabular-nums mt-0.5">
                {tempC.toFixed(1)}&deg;C
              </div>
            </div>
            <div className="bg-stone-50 border border-stone-200 rounded p-3">
              <span className="text-[11px] text-stone-500 font-medium">Soil Air Humidity</span>
              <div className="text-2xl font-bold text-stone-900 font-mono tabular-nums mt-0.5">
                {humidity.toFixed(1)}%
              </div>
            </div>
          </div>
          <p className="text-[11px] text-stone-500 font-medium">
            {humidity > 80 ? '⚠️ High soil saturation detected.' : 'Normal atmospheric baseline.'}
          </p>
        </div>
      </div>
    </div>
  );
};
