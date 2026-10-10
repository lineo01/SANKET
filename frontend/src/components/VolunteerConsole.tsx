import React from 'react';
import { VolunteerDispatch } from '../types';
import { UserCheck, Phone, Shield, Navigation } from 'lucide-react';

interface VolunteerConsoleProps {
  dispatches: VolunteerDispatch[];
}

export const VolunteerConsole: React.FC<VolunteerConsoleProps> = ({ dispatches }) => {
  if (!dispatches || dispatches.length === 0) return null;

  return (
    <div className="bg-white border border-stone-200 rounded-lg p-5 shadow-2xs space-y-4">
      <div className="flex items-center justify-between border-b border-stone-100 pb-3">
        <div>
          <h3 className="text-sm font-bold text-stone-950 flex items-center gap-2">
            <UserCheck className="w-4 h-4 text-emerald-700" />
            Volunteer & Rescue Team Dispatch Assignment
          </h3>
          <p className="text-xs text-stone-500 font-medium mt-0.5">
            Real-time pairing of local Red Cross & Youth Rescuers to critical vulnerable households
          </p>
        </div>
        <span className="inline-flex items-center gap-1.5 text-xs font-semibold px-2.5 py-1 rounded bg-emerald-50 text-emerald-800 border border-emerald-200">
          <span className="w-1.5 h-1.5 rounded-full bg-emerald-600 animate-ping"></span>
          Responders En Route
        </span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {dispatches.map((d) => (
          <div key={d.household_id} className="bg-stone-50 border border-stone-200 rounded-md p-3.5 space-y-2.5 text-xs">
            <div className="flex items-start justify-between">
              <div>
                <span className="font-mono font-bold text-stone-900">{d.household_id}</span>
                <div className="font-semibold text-stone-950 text-sm mt-0.5">{d.head_of_household}</div>
              </div>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-100 text-red-800 border border-red-300">
                {d.predicted_water_depth_m}m FLOOD
              </span>
            </div>

            <div className="bg-white border border-stone-200 rounded p-2 text-stone-600 text-[11px] leading-relaxed">
              <span className="font-semibold text-red-700">जोखिममा रहेका व्यक्ति: </span>
              {d.vulnerability_details}
            </div>

            <div className="border-t border-stone-200 pt-2 space-y-1">
              <div className="flex items-center justify-between text-stone-800 font-semibold">
                <span className="flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5 text-emerald-700" />
                  {d.rescuer.name}
                </span>
                <a href={`tel:${d.rescuer.phone}`} className="flex items-center gap-1 text-emerald-700 hover:underline font-mono">
                  <Phone className="w-3 h-3" />
                  {d.rescuer.phone}
                </a>
              </div>
              <div className="text-[11px] text-stone-500">
                इकाइ: {d.rescuer.org} &bull; उपकरण: <b>{d.rescuer.equipment}</b>
              </div>
              <div className="text-[11px] text-stone-500 flex items-center gap-1 pt-0.5">
                <Navigation className="w-3 h-3 text-sky-600" />
                गन्तव्य: <b>{d.shelter}</b>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};
