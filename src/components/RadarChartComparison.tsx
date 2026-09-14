import { Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer } from "recharts";
import type { DebateSide } from "../types";

function average(side: DebateSide, key: "logic" | "evidence" | "rebuttal_quality") {
  const values = side.claims.map((claim) => claim[key] ?? 0);
  return values.reduce((a, b) => a + b, 0) / values.length;
}
export function RadarChartComparison({ sideA, sideB }: { sideA: DebateSide; sideB: DebateSide }) {
  const data = [
    { metric: "Logic", a: average(sideA, "logic"), b: average(sideB, "logic") },
    { metric: "Evidence", a: average(sideA, "evidence"), b: average(sideB, "evidence") },
    { metric: "Rebuttal", a: average(sideA, "rebuttal_quality"), b: average(sideB, "rebuttal_quality") }
  ];
  return <div className="h-72 w-full"><ResponsiveContainer><RadarChart data={data} outerRadius="69%"><PolarGrid stroke="#dbe3dc" /><PolarAngleAxis dataKey="metric" tick={{ fill: "#69736b", fontSize: 12, fontWeight: 600 }} /><Radar dataKey="a" name={sideA.name} stroke="#3a5c47" fill="#3a5c47" fillOpacity={0.24} strokeWidth={2} /><Radar dataKey="b" name={sideB.name} stroke="#9aa69d" fill="#9aa69d" fillOpacity={0.12} strokeWidth={2} /></RadarChart></ResponsiveContainer></div>;
}
