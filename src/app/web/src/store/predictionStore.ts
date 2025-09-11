import { create } from 'zustand';

export type PanelMode = 'history' | 'nearest';
export type NNMetric = 'euclidean' | 'cosine';

interface PredictionState {
  selectedId: string | null;
  panelMode: PanelMode;
  nnMetric: NNMetric;
  hoverNeighborId: string | null;
  hoverPos: { x: number; y: number } | null;
  setSelectedId: (id: string | null) => void;
  setPanelMode: (mode: PanelMode) => void;
  setNNMetric: (m: NNMetric) => void;
  setHoverNeighbor: (id: string | null, pos?: {x:number;y:number}) => void;
  reset: () => void;
}

// Shared store controlling which prediction is selected and what the side-panel shows.
export const usePredictionStore = create<PredictionState>((set) => ({
  selectedId: null,
  panelMode: 'history',
  nnMetric: 'euclidean',
  hoverNeighborId: null,
  hoverPos: null,
  setSelectedId: (id) => set({ selectedId: id }),
  setPanelMode: (mode) => set({ panelMode: mode }),
  setNNMetric: (m) => set({ nnMetric: m }),
  setHoverNeighbor: (id, pos) => set({ hoverNeighborId: id, hoverPos: pos ?? null }),
  reset: () => set({ selectedId: null, panelMode: 'history' }),
})); 