import { apiRequest } from "@/services/api";
import type {
  DashboardStats,
  Goal,
  GoalCreateRequest,
  GoalUpdateRequest,
} from "@/types";

export const goalService = {
  list(): Promise<Goal[]> {
    return apiRequest<Goal[]>("/api/v1/goals", { auth: true });
  },

  create(data: GoalCreateRequest): Promise<Goal> {
    return apiRequest<Goal>("/api/v1/goals", {
      method: "POST",
      body: data,
      auth: true,
    });
  },

  update(id: number, data: GoalUpdateRequest): Promise<Goal> {
    return apiRequest<Goal>(`/api/v1/goals/${id}`, {
      method: "PATCH",
      body: data,
      auth: true,
    });
  },

  delete(id: number): Promise<void> {
    return apiRequest<void>(`/api/v1/goals/${id}`, {
      method: "DELETE",
      auth: true,
    });
  },

  getDashboardStats(): Promise<DashboardStats> {
    return apiRequest<DashboardStats>("/api/v1/dashboard/stats", { auth: true });
  },
};
