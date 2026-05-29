import React from 'react';
import { ARState } from '../types';

interface DpadControllerProps {
  state: ARState;
  onMove: (dir: 'up' | 'down' | 'left' | 'right') => void;
}

export default function DpadController({
  state,
  onMove,
}: DpadControllerProps) {
  
  // FIX: Movement is only disabled if the building isn't placed OR no floor is selected!
  const isMovementDisabled = !state.isPlaced || state.selectedFloor === 0;

  return (
    <div className="flex flex-col items-center justify-center select-none w-full">
      <div className="text-center mb-2 select-none">
        <h3 className="text-[10px] md:text-xs font-extrabold tracking-[0.18em] text-slate-100 font-sans uppercase leading-none">
          MOVEMENT
        </h3>
        <p className="text-[7.5px] md:text-[8px] font-bold font-mono tracking-widest mt-1 uppercase leading-none">
          {!state.isPlaced ? (
             <span className="text-rose-500">PLACE BLDG FIRST</span>
          ) : state.selectedFloor === 0 ? (
            <span className="text-amber-500">UNAVAILABLE</span>
          ) : (
            <span className="text-emerald-400">FLR {state.selectedFloor} ACTIVE</span>
          )}
        </p>
      </div>

      <div className={`relative w-28 h-28 md:w-36 md:h-36 rounded-full border-2 md:border-3 bg-slate-950/95 flex items-center justify-center transition-all ${
        isMovementDisabled 
          ? 'border-slate-800 opacity-30 pointer-events-none' 
          : 'border-slate-500 hover:border-emerald-400'
      }`}>
        <button onClick={() => !isMovementDisabled && onMove('up')} disabled={isMovementDisabled} className="absolute top-0.5 w-10 h-8 md:w-12 md:h-10 flex items-center justify-center rounded-t-full hover:bg-white/10 active:bg-white/15 text-slate-100 disabled:pointer-events-none">
          <svg className="w-5 h-5 md:w-6 md:h-6 pointer-events-none active:scale-95" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M5 15l7-7 7 7" /></svg>
        </button>
        <button onClick={() => !isMovementDisabled && onMove('left')} disabled={isMovementDisabled} className="absolute left-0.5 w-8 h-10 md:w-10 md:h-12 flex items-center justify-center rounded-l-full hover:bg-white/10 active:bg-white/15 text-slate-100 disabled:pointer-events-none">
          <svg className="w-5 h-5 md:w-6 md:h-6 pointer-events-none active:scale-95" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" /></svg>
        </button>
        <button onClick={() => !isMovementDisabled && onMove('right')} disabled={isMovementDisabled} className="absolute right-0.5 w-8 h-10 md:w-10 md:h-12 flex items-center justify-center rounded-r-full hover:bg-white/10 active:bg-white/15 text-slate-100 disabled:pointer-events-none">
          <svg className="w-5 h-5 md:w-6 md:h-6 pointer-events-none active:scale-95" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" /></svg>
        </button>
        <button onClick={() => !isMovementDisabled && onMove('down')} disabled={isMovementDisabled} className="absolute bottom-0.5 w-10 h-8 md:w-12 md:h-10 flex items-center justify-center rounded-b-full hover:bg-white/10 active:bg-white/15 text-slate-100 disabled:pointer-events-none">
          <svg className="w-5 h-5 md:w-6 md:h-6 pointer-events-none active:scale-95" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth="2.5"><path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" /></svg>
        </button>

        <div className="w-6 h-6 md:w-8 md:h-8 rounded-full border border-slate-650 bg-slate-950 flex items-center justify-center">
          <div className={`w-2 h-2 md:w-2.5 md:h-2.5 rounded-full ${isMovementDisabled ? 'bg-slate-700' : 'bg-cyan-400'}`} />
        </div>
      </div>
    </div>
  );
}