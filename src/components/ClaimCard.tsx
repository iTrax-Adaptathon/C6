import { animate, motion, useMotionValue, useMotionValueEvent } from "framer-motion";
import { ChevronDown, MessageSquareText } from "lucide-react";
import { useEffect, useState } from "react";
import { Card } from "./ui/card";
import type { Claim } from "../types";

function Score({ value }: { value: number | null }) {
  const motionValue = useMotionValue(0);
  const [display, setDisplay] = useState(0);
  useEffect(() => { motionValue.set(0); const controls = animate(motionValue, value ?? 0, { duration: 0.8, ease: "easeOut" }); return () => controls.stop(); }, [motionValue, value]);
  useMotionValueEvent(motionValue, "change", (latest) => setDisplay(latest));
  return <span className="text-base font-bold tabular-nums text-foreground">{value === null ? "—" : display.toFixed(1)}</span>;
}
export function ClaimCard({ claim, index }: { claim: Claim; index: number }) {
  const [open, setOpen] = useState(false);
  return <Card className="overflow-hidden"><button onClick={() => setOpen(!open)} aria-expanded={open} className="flex w-full items-start gap-3 p-4 text-left"><span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-bold text-muted-foreground">{index + 1}</span><span className="flex-1 text-sm font-medium leading-6">{claim.text}</span><ChevronDown className={`mt-1 shrink-0 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`} size={18} /></button>{open && <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} className="border-t border-border"><div className="grid grid-cols-3 gap-2 p-4"><Metric label="Logic" value={claim.logic} /><Metric label="Evidence" value={claim.evidence} /><Metric label="Rebuttal" value={claim.rebuttal_quality} /></div><div className="mx-4 mb-4 flex gap-2 rounded-xl bg-muted p-3 text-xs leading-5 text-muted-foreground"><MessageSquareText size={15} className="mt-0.5 shrink-0 text-primary" />{claim.note}</div></motion.div>}</Card>;
}
function Metric({ label, value }: { label: string; value: number | null }) { return <div className="rounded-lg bg-muted px-2 py-2 text-center"><p className="text-[10px] font-bold uppercase tracking-wide text-muted-foreground">{label}</p><Score value={value} /></div>; }
