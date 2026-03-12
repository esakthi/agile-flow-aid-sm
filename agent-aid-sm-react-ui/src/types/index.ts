export interface DashboardResponse {
  role: string;
  summary: string;
  metrics: Record<string, any>;
  visualisations: VisualisationSpec[];
  drilldowns: {
    epic_to_story: boolean;
    story_to_commit: boolean;
    commit_to_build: boolean;
    build_to_acceptance: boolean;
  };
  alerts: Alert[];
}

export interface VisualisationSpec {
  type: string;
  title: string;
  data_source: string;
}

export interface Alert {
  severity: 'high' | 'medium' | 'low';
  message: string;
}

export interface ChatResponse {
  response: string;
  role: string;
  voice_summary?: string;
  grounding_metadata?: any;
}
