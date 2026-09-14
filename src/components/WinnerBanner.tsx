import { motion } from "framer-motion";
import { Scale } from "lucide-react";
import { Badge } from "./ui/badge";
import type { Verdict } from "../types";

export function WinnerBanner({ verdict }: { verdict: Verdict }) {
  const close = verdict.winner === "close" || Math.abs(verdict.sideA.overall_score - verdict.sideB.overall_score) < 0.5;
  const winner = verdict.winner === "sideA" ? verdict.sideA : verdict.sideB;
  return <motion.section initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} className="overflow-hidden rounded-3xl border border-border bg-white shadow-sm">
    <div className="flex flex-col gap-5 p-6 sm:flex-row sm:items-center sm:justify-between sm:p-8"><div className="flex items-start gap-4"><div className="rounded-2xl bg-primary/10 p-3 text-primary"><Scale size={23} /></div><div><Badge className={close ? "bg-muted text-muted-foreground" : "bg-primary/10 text-primary"}>{close ? "Narrow margin" : "Judgment delivered"}</Badge><h1 className="mt-2 font-serif text-3xl font-semibold tracking-tight sm:text-4xl">{close ? "Closely contested" : `${winner.name} wins`}</h1><p className="mt-1 text-sm text-muted-foreground">{close ? "The arguments were separated by less than half a point." : "A clearer case on balance of argument."}</p></div></div><div className="rounded-2xl bg-muted px-5 py-4 text-right"><p className="text-[11px] font-bold uppercase tracking-[.16em] text-muted-foreground">Overall score</p><p className="mt-1 text-2xl font-bold tabular-nums">{verdict.sideA.overall_score.toFixed(1)} <span className="text-muted-foreground">vs</span> {verdict.sideB.overall_score.toFixed(1)}</p></div></div>
  </motion.section>;
}
