import { apiRequest } from "@/services/api";
import type { Mission } from "@/types";

export const missionService = {
  listToday(): Promise<Mission[]> {
    return apiRequest<Mission[]>("/api/v1/missions/today", { auth: true });
  },

  listAll(): Promise<Mission[]> {
    return apiRequest<Mission[]>("/api/v1/missions", { auth: true });
  },

  complete(id: number, notes?: string): Promise<Mission> {
    return apiRequest<Mission>(`/api/v1/missions/${id}/complete`, {
      method: "POST",
      body: notes ? { notes } : {},
      auth: true,
    });
  },

  fail(id: number, notes?: string): Promise<Mission> {
    return apiRequest<Mission>(`/api/v1/missions/${id}/fail`, {
      method: "POST",
      body: notes ? { notes } : {},
      auth: true,
    });
  },
};
