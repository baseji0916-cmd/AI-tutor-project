import { apiRequest } from "@/services/api";
import type { TimelineEvent } from "@/types";

export const timelineService = {
  list(): Promise<TimelineEvent[]> {
    return apiRequest<TimelineEvent[]>("/api/v1/timeline", { auth: true });
  },
};
