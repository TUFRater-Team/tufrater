// Interface type structure matching the response from "/files/upload"
export interface PredictionResponse {
  difficulty: string;
  raw_score: number;
  features: {
    tilecount: number;
    bpm: number;
    twirl_count: number;
    speed_change_count: number;
    s_norm: number;
    rt_score: number;
    p_var: number;
  };
}
