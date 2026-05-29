import React from 'react';
import { RotateCw } from 'lucide-react';
import { ARState } from '../types';
import DpadController from './DpadController'; // Automatically pulls the clean D-Pad from above

interface FloorSelectorProps {
  state: ARState;
  isOpen: boolean;
  onToggle: () => void;
  onSelectFloor: (floor: number) => void;
  onResetFloor: () => void;
  onMove: (dir: 'up' | 'down' | 'left' | 'right') => void;
}

export default function FloorSelector({
  state,
  isOpen,
  onToggle,
  onSelectFloor,
  onResetFloor,
  onMove,
}: FloorSelectorProps) {
  return (
    <div className="flex flex-col-reverse items-center select-none w-full">
      
      {/* 1. NAV Toggle Trigger */}
      <div className="flex flex-col items-center mt-1 w-full">
        <button
          onClick={onToggle}
          aria-label="Toggle Navigation and Movement Controls"
          className={`flex items-center justify-center w-14 h-14 md:w-[72px] md:h-[72px] rounded-xl border-2 transition-colors bg-slate-950/95 ${
            isOpen ? 'border-emerald-500 shadow-[0_0_10px_rgba(16,185,129,0.2)]' : 'border-slate-400 hover:border-emerald-400'
          }`}
        >
          <div className="relative flex items-center justify-center w-9 h-9 md:w-11 md:h-11 border-2 border-slate-400 rounded-lg bg-slate-900/60">
            <svg className="w-6 h-6 md:w-8 md:h-8 text-slate-100" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 4L6 18l6-3 6 3-6-14z" />
              <circle cx="12" cy="18" r="1.5" fill="currentColor" />
            </svg>
            <span className="absolute -top-1 -right-1 flex h-2 w-2">
              <span className="relative inline-flex rounded-full h-2 w-2 bg-cyan-500"></span>
            </span>
          </div>
        </button>
        <span className="text-[9px] md:text-[10px] font-extrabold tracking-[0.15em] text-slate-100 mt-1 uppercase font-sans leading-none text-center">NAV</span>
      </div>

      {/* 2. Collapsible Container containing BOTH Dpad Controller and 2x2 Floor Grid */}
      {isOpen && (
        <div className="flex flex-col-reverse items-center w-full">
          <div className="w-[2px] h-3 md:h-4 bg-slate-400" />
          
          <div className="p-3 md:p-4 bg-slate-950/95 rounded-2xl border-2 border-slate-700/80 shadow-2xl flex flex-col items-center justify-center w-full max-w-[160px] md:max-w-[210px] gap-3">
            
            {/* DPAD CONTROLLER INJECTED HERE */}
            <DpadController state={state} onMove={onMove} />

            <div className="w-full h-[1px] bg-slate-800" />

            {/* 2x2 Grid of Floor Buttons */}
            <div className="grid grid-cols-2 gap-1.5 md:gap-2 w-full">
              <button
                onClick={() => onSelectFloor(1)}
                className={`flex flex-col items-center justify-center w-full h-11 md:h-[48px] rounded-lg border-2 ${
                  state.selectedFloor === 1 ? 'border-emerald-500 bg-emerald-950/20 text-emerald-400 font-extrabold' : 'border-slate-500 bg-slate-900/40 text-slate-300 hover:border-slate-100 hover:text-white'
                }`}
              >
                <span className="text-sm md:text-base leading-none">↑</span>
                <span className="text-[8px] md:text-[9.5px] font-extrabold tracking-wider mt-0.5">FLR 1</span>
              </button>

              <button
                onClick={() => onSelectFloor(2)}
                className={`flex flex-col items-center justify-center w-full h-11 md:h-[48px] rounded-lg border-2 ${
                  state.selectedFloor === 2 ? 'border-emerald-400 bg-emerald-950/25 text-emerald-300 font-extrabold' : 'border-slate-500 bg-slate-900/40 text-slate-300 hover:border-slate-100 hover:text-white'
                }`}
              >
                <span className="text-xs md:text-xs leading-none flex items-center justify-center w-3 h-2.5">
                  <svg className="w-3.5 h-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="3">
                    <path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" />
                  </svg>
                </span>
                <span className="text-[8px] md:text-[9.5px] font-extrabold tracking-wider mt-0.5">FLR 2</span>
              </button>

              <button
                onClick={() => onSelectFloor(3)}
                className={`flex flex-col items-center justify-center w-full h-11 md:h-[48px] rounded-lg border-2 ${
                  state.selectedFloor === 3 ? 'border-emerald-500 bg-emerald-950/20 text-emerald-400 font-extrabold' : 'border-slate-500 bg-slate-900/40 text-slate-300 hover:border-slate-100 hover:text-white'
                }`}
              >
                <span className="text-sm md:text-base leading-none">↑</span>
                <span className="text-[8px] md:text-[9.5px] font-extrabold tracking-wider mt-0.5">FLR 3</span>
              </button>

              <button
                onClick={onResetFloor}
                className={`flex flex-col items-center justify-center w-full h-11 md:h-[48px] rounded-lg border-2 ${
                  state.selectedFloor === 0 ? 'border-cyan-500 bg-cyan-950/20 text-cyan-400 font-bold' : 'border-slate-500 bg-slate-900/40 text-slate-400 hover:border-slate-100 hover:text-white'
                }`}
              >
                <div className="flex items-center justify-center relative w-[14px] h-[14px] md:w-[18px] md:h-[18px] rounded-full border border-slate-450 bg-slate-950/80">
                  <RotateCw className="w-2 h-2 md:w-2.5 md:h-2.5 text-slate-300" />
                  <span className="absolute text-[5px] md:text-[5.5px] font-bold text-cyan-400 font-mono">R</span>
                </div>
                <span className="text-[7px] md:text-[7.5px] font-extrabold tracking-tighter mt-0.5 text-slate-300 uppercase leading-none text-center">RESET</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}