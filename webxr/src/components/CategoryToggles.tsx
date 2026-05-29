import React, { useState } from 'react';
import { Layers } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import { ARState } from '../types';

interface LayerControlsProps {
  state: ARState;
  isOpen: boolean;
  onToggle: () => void;
  onToggleLayer: (layerKey: keyof ARState['layers']) => void;
}

export default function LayerControls({
  state,
  onToggleLayer,
}: LayerControlsProps) {
  // Collapse/Expand state default to true to match photo initial state
  const [isOpen, setIsOpen] = useState(true);

  return (
    <div className="flex flex-col-reverse items-center select-none">
      
      {/* 2. LAYERS Toggle Trigger Module */}
      <div className="flex flex-col items-center mt-1">
        <button
          onClick={() => setIsOpen(!isOpen)}
          aria-label="Toggle Layers Controls List"
          className={`flex items-center justify-center w-14 h-14 md:w-[72px] md:h-[72px] rounded-xl border-2 transition-all bg-slate-950/90 active:scale-95 shadow-lg ${
            isOpen 
              ? 'border-emerald-500 shadow-[0_0_12px_rgba(16,185,129,0.3)]' 
              : 'border-slate-400 hover:border-emerald-400'
          }`}
        >
          {/* Custom Layers outline box symbol */}
          <div className="relative flex items-center justify-center w-9 h-9 md:w-11 md:h-11 border-2 border-slate-400 rounded-lg bg-slate-900/60">
            <Layers className="w-5 h-5 md:w-6 md:h-6 text-slate-100" />
            
            {/* Pulsing indicator light */}
            <span className="absolute -top-1 -right-1 flex h-2.5 w-2.5">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-400"></span>
            </span>
          </div>
        </button>

        <span className="text-[9px] md:text-[10px] font-extrabold tracking-[0.15em] text-slate-100 mt-1 uppercase font-sans leading-none">
          LAYERS
        </span>
      </div>

      {/* 1. Collapsible List of Layer Toggles */}
      <AnimatePresence initial={false}>
        {isOpen && (
          <div className="flex flex-col-reverse items-center">
            
            {/* Direct vertical wire line connecting toggles to LAYERS button */}
            <motion.div
              initial={{ scaleY: 0, opacity: 0 }}
              animate={{ scaleY: 1, opacity: 1 }}
              exit={{ scaleY: 0, opacity: 0 }}
              transition={{ duration: 0.2 }}
              className="w-[2px] h-3 md:h-4 bg-slate-400 origin-bottom"
            />

            {/* Outlined container holding the 2x2 grid of buttons */}
            <motion.div
              initial={{ y: 15, opacity: 0, scale: 0.95 }}
              animate={{ y: 0, opacity: 1, scale: 1 }}
              exit={{ y: 15, opacity: 0, scale: 0.95 }}
              transition={{ duration: 0.2 }}
              className="p-2 md:p-3 bg-slate-950/90 backdrop-blur-md rounded-2xl border-2 border-slate-700/80 shadow-2xl flex items-center justify-center"
            >
              <div className="grid grid-cols-2 gap-1.5 md:gap-2.5">
                {/* Foundations */}
                <button
                  onClick={() => onToggleLayer('foundations')}
                  className={`flex flex-col items-center justify-center w-14 h-11 md:w-[68px] md:h-[48px] rounded-lg border-2 transition-all ${
                    state.layers.foundations
                      ? 'border-emerald-500 bg-emerald-950/20 text-emerald-400 font-extrabold shadow-[0_0_8px_rgba(16,185,129,0.3)]'
                      : 'border-slate-500 bg-slate-900/40 text-slate-300 hover:border-slate-100 hover:text-white'
                  }`}
                >
                  <span className="text-xs md:text-sm font-semibold leading-none text-cyan-400">⨁</span>
                  <span className="text-[8px] md:text-[9.5px] font-extrabold tracking-wider mt-1 uppercase">FOUND</span>
                </button>

                {/* Columns */}
                <button
                  onClick={() => onToggleLayer('columns')}
                  className={`flex flex-col items-center justify-center w-14 h-11 md:w-[68px] md:h-[48px] rounded-lg border-2 transition-all ${
                    state.layers.columns
                      ? 'border-emerald-400 bg-emerald-950/25 text-emerald-300 font-extrabold shadow-[0_0_10px_rgba(16,185,129,0.4)]'
                      : 'border-slate-500 bg-slate-900/40 text-slate-300 hover:border-slate-100 hover:text-white'
                  }`}
                >
                  <span className="text-xs md:text-sm font-semibold leading-none text-emerald-400">‖</span>
                  <span className="text-[8px] md:text-[9.5px] font-extrabold tracking-wider mt-1 uppercase">COLS</span>
                </button>

                {/* Beams */}
                <button
                  onClick={() => onToggleLayer('beams')}
                  className={`flex flex-col items-center justify-center w-14 h-11 md:w-[68px] md:h-[48px] rounded-lg border-2 transition-all ${
                    state.layers.beams
                      ? 'border-emerald-500 bg-emerald-950/20 text-emerald-400 font-extrabold shadow-[0_0_8px_rgba(16,185,129,0.3)]'
                      : 'border-slate-500 bg-slate-900/40 text-slate-300 hover:border-slate-100 hover:text-white'
                  }`}
                >
                  <span className="text-xs md:text-sm font-semibold leading-none text-amber-500">═</span>
                  <span className="text-[8px] md:text-[9.5px] font-extrabold tracking-wider mt-1 uppercase">BEAM</span>
                </button>

                {/* Floors */}
                <button
                  onClick={() => onToggleLayer('floors')}
                  className={`flex flex-col items-center justify-center w-14 h-11 md:w-[68px] md:h-[48px] rounded-lg border-2 transition-all ${
                    state.layers.floors
                      ? 'border-emerald-500 bg-emerald-950/20 text-emerald-400 font-extrabold shadow-[0_0_8px_rgba(16,185,129,0.3)]'
                      : 'border-slate-500 bg-slate-900/40 text-slate-300 hover:border-slate-100 hover:text-white'
                  }`}
                >
                  <span className="text-xs md:text-sm font-semibold leading-none text-purple-400">≡</span>
                  <span className="text-[8px] md:text-[9.5px] font-extrabold tracking-wider mt-1 uppercase">FLRS</span>
                </button>
              </div>
            </motion.div>

          </div>
        )}
      </AnimatePresence>

    </div>
  );
}
