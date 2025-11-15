const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export interface DashboardResponse {
  message: string;
  html: string | null;
}

export const apiClient = {
  async sendChatMessage(content: string): Promise<DashboardResponse> {
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ content }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Chat API error:", error);
      throw error;
    }
  },

  async getSampleDashboard(): Promise<DashboardResponse> {
    try {
      const response = await fetch(`${API_URL}/dashboard/sample`);

      if (!response.ok) {
        throw new Error(`API error: ${response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      console.error("Sample dashboard API error:", error);
      throw error;
    }
  },
};
