export interface Claim { text: string; logic: number; evidence: number; rebuttal_quality: number | null; note: string; }
export interface DebateSide { name: string; claims: Claim[]; overall_score: number; }
export interface Verdict { topic: string; sideA: DebateSide; sideB: DebateSide; winner: "sideA" | "sideB" | "close"; reasoning: string; }
