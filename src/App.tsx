import { AnimatePresence, motion } from "framer-motion";
import { useState } from "react";
import { InputScreen, type InputValues } from "./components/InputScreen";
import { VerdictDashboard } from "./components/VerdictDashboard";
import { mockVerdict } from "./data/mockVerdict";
import type { Verdict } from "./types";

async function judgeDebate(_input: InputValues): Promise<Verdict> {
  // Swap the next line for: return fetch("/judge", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(_input) }).then(r => r.json());
  await new Promise((resolve) => window.setTimeout(resolve, 3600));
  return { ...mockVerdict, topic: _input.topic.trim() || mockVerdict.topic };
}
export default function App() { const [verdict, setVerdict] = useState<Verdict | null>(null); return <AnimatePresence mode="wait">{verdict ? <motion.div key="verdict" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}><VerdictDashboard verdict={verdict} onReset={() => setVerdict(null)} /></motion.div> : <motion.div key="input" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}><InputScreen onSubmit={async (values) => setVerdict(await judgeDebate(values))} /></motion.div>}</AnimatePresence>; }
