export interface ChatMessage {
  id: number;
  sender: "user" | "bot";
  message: string;
}

export interface DashboardChart {
  type: "bar" | "line" | "pie" | "area";
  title: string;
  xAxis?: string;
  yAxis?: string;
  dataKey: string;
}

export interface DashboardSpec {
  title: string;
  description: string;
  intent?: string;
  charts: DashboardChart[];
}

export interface DashboardData {
  [key: string]: Record<string, string | number | boolean>[];
}

export interface DashboardResponse {
  message: string;
  dashboard_spec?: DashboardSpec;
  data?: DashboardData;
}

export interface ApiChatRequest {
  content: string;
}
