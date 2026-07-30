import { motion, AnimatePresence } from 'framer-motion';
import { useState, useEffect } from 'react';
import { useForgeStore } from '../store/useForgeStore';

const steps = [
  'Booting Forge OS core engine...',
  'Loading autonomous AI workforce...',
  'Connecting FastAPI provider router...',
  'Indexing lead intelligence database...',
  'Synthesizing daily opportunity brief...',
  'Forge OS V6 ready.',
];

export function BootScreen() {
  const [step, setStep] = useState(0);
  const setBooted = useForgeStore((s) => s.setBooted);

  useEffect(() => {
    const t = setInterval(() => {
      setStep((prev) => {
        if (prev >= steps.length - 1) {
          clearInterval(t);
          setTimeout(() => setBooted(true), 600);
          return prev;
        }
        return prev + 1;
      });
    }, 400);
    return () => clearInterval(t);
  }, [setBooted]);

  const progress = ((step + 1) / steps.length) * 100;

  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      exit={{ opacity: 0 }}
      className="fixed inset-0 flex flex-col items-center justify-center"
      style={{ background: 'var(--bg-base)' }}
    >
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
        className="w-full max-w-sm px-8"
      >
        {/* Wordmark */}
        <div className="mb-12 text-center">
          <div className="flex items-center justify-center gap-3 mb-3">
            <div
              className="w-10 h-10 rounded-xl flex items-center justify-center text-lg font-black"
              style={{ background: 'var(--primary)', color: 'white', boxShadow: '0 0 32px var(--primary-glow)' }}
            >
              F
            </div>
            <div className="text-left">
              <div className="text-xl font-bold" style={{ color: 'var(--text-primary)' }}>Forge OS</div>
              <div className="label" style={{ color: 'var(--text-tertiary)' }}>V6 · AI OPERATING SYSTEM</div>
            </div>
          </div>
        </div>

        {/* Step text */}
        <div className="mb-5 h-5">
          <AnimatePresence mode="wait">
            <motion.p
              key={step}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.25 }}
              className="mono text-xs text-center"
              style={{ color: step === steps.length - 1 ? 'var(--success)' : 'var(--text-secondary)' }}
            >
              {steps[step]}
            </motion.p>
          </AnimatePresence>
        </div>

        {/* Progress bar */}
        <div
          className="w-full h-1 rounded-full overflow-hidden"
          style={{ background: 'var(--bg-surface-2)' }}
        >
          <motion.div
            className="h-full rounded-full"
            style={{ background: 'var(--primary)' }}
            initial={{ width: '0%' }}
            animate={{ width: `${progress}%` }}
            transition={{ duration: 0.35, ease: 'easeOut' }}
          />
        </div>

        {/* Footer meta */}
        <div className="mt-4 flex justify-between">
          <span className="mono" style={{ fontSize: 10, color: 'var(--text-tertiary)' }}>React 18 + Vite + FastAPI</span>
          <span className="mono" style={{ fontSize: 10, color: 'var(--text-tertiary)' }}>{Math.round(progress)}%</span>
        </div>
      </motion.div>
    </motion.div>
  );
}
