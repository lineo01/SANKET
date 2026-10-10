import React, { useEffect, useRef } from 'react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';
import { TriageHousehold } from '../types';

interface FloodMapProps {
  households: TriageHousehold[];
  selectedZoneFilter?: string;
}

export const FloodMap: React.FC<FloodMapProps> = ({ households, selectedZoneFilter }) => {
  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapInstanceRef = useRef<L.Map | null>(null);
  const householdLayerRef = useRef<L.LayerGroup | null>(null);

  useEffect(() => {
    const container = mapContainerRef.current;
    if (!container) return;

    // Fix: Clear existing Leaflet ID to prevent "Map container is already initialized" crash in React 18
    if ((container as any)._leaflet_id) {
      (container as any)._leaflet_id = null;
    }

    const map = L.map(container, {
      center: [27.9960, 81.8790],
      zoom: 14,
      zoomControl: true,
    });
    mapInstanceRef.current = map;

    // OpenStreetMap Light Tiles (Zero API key needed)
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; OpenStreetMap contributors',
      maxZoom: 19,
    }).addTo(map);

    setTimeout(() => {
      map.invalidateSize();
    }, 200);

    const riverLayer = L.layerGroup().addTo(map);
    const shelterLayer = L.layerGroup().addTo(map);
    const householdLayer = L.layerGroup().addTo(map);
    householdLayerRef.current = householdLayer;

    // 1. Draw River System
    fetch('/api/river/geojson')
      .then(res => res.json())
      .then(data => {
        if (!data.features) return;
        data.features.forEach((feat: any) => {
          const coords = feat.geometry.coordinates.map((c: [number, number]) => [c[1], c[0]]);
          const p = feat.properties;
          const isMain = p.type === 'main_river';

          L.polyline(coords, {
            color: isMain ? '#38bdf8' : '#7dd3fc',
            weight: isMain ? 12 : 7,
            opacity: 0.65,
            lineCap: 'round',
          }).addTo(riverLayer);

          L.polyline(coords, {
            color: isMain ? '#0284c7' : '#0369a1',
            weight: isMain ? 4 : 2.5,
            opacity: 0.95,
            dashArray: isMain ? undefined : '5, 5',
          }).bindPopup(`<b>${p.river_name}</b>`).addTo(riverLayer);
        });
      })
      .catch(() => {});

    // 2. Draw Shelters
    fetch('/api/shelters/geojson')
      .then(res => res.json())
      .then(data => {
        if (!data.features) return;
        data.features.forEach((feat: any) => {
          const [lng, lat] = feat.geometry.coordinates;
          const p = feat.properties;

          const shelterIcon = L.divIcon({
            className: 'custom-shelter',
            html: `<div style="background-color:#059669; color:#ffffff; padding:4px 8px; border-radius:6px; font-weight:700; font-size:10.5px; border:2px solid #ffffff; box-shadow:0 2px 8px rgba(0,0,0,0.25); display:flex; align-items:center; gap:4px; white-space:nowrap;">
                    <span>🏫</span>
                    <span>${p.name_en || p.name}</span>
                   </div>`,
            iconSize: [160, 26],
            iconAnchor: [80, 13],
          });

          L.marker([lat, lng], { icon: shelterIcon })
            .bindPopup(`<b>${p.name}</b><br/>Capacity: ${p.capacity_people} persons`)
            .addTo(shelterLayer);
        });
      })
      .catch(() => {});

    // Cleanup on unmount to prevent React 18 re-mount crash
    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, []);

  // Update household risk circles whenever households or filter changes
  useEffect(() => {
    if (!householdLayerRef.current || !mapInstanceRef.current) return;
    householdLayerRef.current.clearLayers();
    mapInstanceRef.current.invalidateSize();

    const filtered = selectedZoneFilter && selectedZoneFilter !== 'ALL'
      ? households.filter(h => h.zone === selectedZoneFilter)
      : households;

    filtered.forEach((h) => {
      const lat = h.latitude ?? 27.9892;
      const lng = h.longitude ?? 81.8761;
      const depth = h.predicted_water_depth_m;
      const collapse = h.structural_collapse_threat;

      let fillColor = '#16a34a';
      let strokeColor = '#15803d';
      let radius = 6;

      if (collapse || depth >= 1.5) {
        fillColor = '#dc2626';
        strokeColor = '#991b1b';
        radius = 11;
      } else if (depth >= 0.5) {
        fillColor = '#ea580c';
        strokeColor = '#c2410c';
        radius = 8.5;
      } else if (depth > 0) {
        fillColor = '#eab308';
        strokeColor = '#a16207';
        radius = 6.5;
      }

      const circle = L.circleMarker([lat, lng], {
        radius: radius,
        fillColor: fillColor,
        color: strokeColor,
        weight: 2,
        opacity: 0.95,
        fillOpacity: 0.85,
      });

      circle.bindPopup(`
        <div style="font-family:sans-serif; font-size:12px; color:#1e293b; line-height:1.4; min-width:210px;">
          <div style="border-bottom:1px solid #e2e8f0; padding-bottom:3px; margin-bottom:4px;">
            <strong style="color:#0f172a; font-size:13px;">${h.head_of_household || h.household_id}</strong>
          </div>
          <div>Flood Depth: <b style="color:${depth > 0 ? '#dc2626' : '#15803d'}">${depth}m</b></div>
          <div>Vulnerabilities: <span style="color:#b91c1c;">${h.vulnerability_details || 'सामान्य'}</span></div>
          <div>Assigned Shelter: <b style="color:#059669;">${h.nearest_shelter}</b></div>
        </div>
      `);

      householdLayerRef.current?.addLayer(circle);
    });
  }, [households, selectedZoneFilter]);

  return (
    <div className="relative w-full h-[470px] rounded-lg overflow-hidden border border-stone-200 bg-stone-50 shadow-sm">
      <div ref={mapContainerRef} className="w-full h-full z-0" />
      <div className="absolute bottom-4 right-4 z-[1000] bg-white/95 backdrop-blur border border-stone-300 rounded-md p-3 text-[11px] shadow-sm text-stone-700 space-y-1.5">
        <div className="font-semibold text-stone-900 border-b border-stone-200 pb-1 mb-1 tracking-tight">
          Spatial GIS Layers
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-red-600 border border-red-700" />
          <span>Severe / Collapse Risk (&ge; 1.5m or Kachha)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-orange-600 border border-orange-700" />
          <span>Moderate Inundation (0.5m &ndash; 1.5m)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-3 h-3 rounded-full bg-emerald-600 border border-emerald-700" />
          <span>Dry / Safe Footprint (0.0m)</span>
        </div>
        <div className="flex items-center gap-2 pt-1 border-t border-stone-200">
          <span className="px-1.5 py-0.2 bg-emerald-700 text-white rounded font-bold text-[9px]">🏫</span>
          <span>4 Evacuation Shelters</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="w-4 h-1 bg-sky-600 rounded" />
          <span>West Rapti River & Tributaries</span>
        </div>
      </div>
    </div>
  );
};
