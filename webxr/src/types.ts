export interface ARState {
  scale: number;
  opacity: number;
  posX: number;
  posY: number;
  rotation: number;
  selectedFloor: number; // 1, 2, 3
  isArMode: boolean;
  isLocked: boolean;
  isPlaced: boolean;
  layers: {
    foundations: boolean;
    columns: boolean;
    beams: boolean;
    floors: boolean;
  };
}

export type ActionLog = {
  id: string;
  timestamp: string;
  message: string;
};
