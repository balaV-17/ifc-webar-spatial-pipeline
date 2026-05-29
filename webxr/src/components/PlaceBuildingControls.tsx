import React from 'react';
import { ARState } from '../types';

interface PlaceBuildingControlsProps {
  state: ARState;
  onChangeState: (updater: (prev: ARState) => ARState) => void;
}

export default function PlaceBuildingControls({
  state,
  onChangeState,
}: PlaceBuildingControlsProps) {
  
  const handleTogglePlace = () => {
    onChangeState((prev) => {
      // FIX: We only toggle isPlaced. We no longer force isLocked to true!
      return {
        ...prev,
        isPlaced: !prev.isPlaced,
      };
    });
  };

  return (
    <div className="bg-slate-950/95 p-1.5 md:p-2.5 rounded-2xl border-2 border-slate-700/80 select-none w-full max-w-[150px] md:max-w-[210px] flex flex-col justify-center items-center shadow-lg">
      <button
        onClick={handleTogglePlace}
        className={`w-full py-2 px-3 rounded-xl border-2 font-extrabold text-[10px] md:text-xs tracking-[0.1em] cursor-pointer select-none transition-all ${
          state.isPlaced
            ? 'border-emerald-500 bg-emerald-950/20 text-emerald-400 font-black shadow-[0_0_10px_rgba(16,185,129,0.25)] hover:border-emerald-400'
            : 'border-slate-400 bg-slate-900/60 text-slate-100 hover:border-cyan-400 hover:text-cyan-400'
        }`}
      >
        {state.isPlaced ? 'BUILDING PLACED' : 'PLACE BUILDING'}
      </button>
    </div>
  );
}