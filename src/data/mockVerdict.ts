import type { Verdict } from "../types";

export const mockVerdict: Verdict = {
  topic: "Should cities restrict private cars in downtown areas?",
  sideA: { name: "Side A", overall_score: 7.1, claims: [
    { text: "Car-light centers give people room back for walking, cycling, and local life.", logic: 8.2, evidence: 7.4, rebuttal_quality: 7.6, note: "A clear causal case that connects street design to public benefit." },
    { text: "Congestion pricing has reduced traffic in comparable city centers.", logic: 7.5, evidence: 8.1, rebuttal_quality: 7.1, note: "Strong use of precedent, though implementation differences are worth noting." },
    { text: "Exemptions and better transit can protect workers with limited options.", logic: 6.9, evidence: 6.7, rebuttal_quality: 7.8, note: "Directly addresses the equity objection with practical safeguards." }
  ] },
  sideB: { name: "Side B", overall_score: 5.8, claims: [
    { text: "Small businesses depend on customers being able to drive and park nearby.", logic: 6.8, evidence: 5.4, rebuttal_quality: 5.9, note: "Plausible concern, but presented without local business data." },
    { text: "Restrictions can burden people who live outside reliable transit networks.", logic: 7.2, evidence: 6.1, rebuttal_quality: 6.3, note: "A meaningful fairness point that needed a more developed alternative." },
    { text: "Delivery and emergency access make a full restriction impractical.", logic: 6.1, evidence: 5.7, rebuttal_quality: 5.4, note: "Useful qualification, but it does not refute a policy with exemptions." }
  ] },
  winner: "sideA",
  reasoning: "Side A offered the more complete case. Its argument connected a concrete policy mechanism to broader civic outcomes, then answered the strongest equity concerns with specific accommodations. Side B raised important cautions, especially around access and small businesses, but did not provide enough evidence or a competing framework to outweigh the case for a carefully designed restriction."
};
