import { cva, type VariantProps } from "class-variance-authority";
import type { ButtonHTMLAttributes } from "react";
import { cn } from "../../lib/utils";

const buttonVariants = cva("inline-flex items-center justify-center gap-2 rounded-xl text-sm font-semibold transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/30 disabled:pointer-events-none disabled:opacity-45", { variants: { variant: { default: "bg-primary text-primary-foreground shadow-[0_8px_20px_rgba(58,92,71,.18)] hover:bg-primary/90", outline: "border border-border bg-white text-foreground hover:bg-muted", ghost: "text-muted-foreground hover:bg-muted hover:text-foreground" }, size: { default: "h-11 px-5", sm: "h-9 px-3.5 text-xs", lg: "h-12 px-6" } }, defaultVariants: { variant: "default", size: "default" } });

export interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement>, VariantProps<typeof buttonVariants> {}
export function Button({ className, variant, size, ...props }: ButtonProps) { return <button className={cn(buttonVariants({ variant, size }), className)} {...props} />; }
