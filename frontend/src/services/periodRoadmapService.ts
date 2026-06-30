import { apiRequest } from "@/services/api";
import type { PeriodRoadmap } from "@/types";

export const periodRoadmapService = {
  get(): Promise<PeriodRoadmap> {
    return apiRequest<PeriodRoadmap>("/api/v1/dashboard/period-roadmap", {
      auth: true,
    });
  },
};
