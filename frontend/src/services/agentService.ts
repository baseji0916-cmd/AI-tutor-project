import { apiRequest } from "@/services/api";
import type {
  AutoReplanResult,
  CoachFeedback,
  FailureRecovery,
  FutureSimulation,
  GeneratePlanResult,
  GoalAnalysis,
  GrowthDNAProfile,
  GrowthPredictor,
  GrowthStory,
  PersonalityInfo,
  Recommendations,
  TimelineEvent,
} from "@/types";

const AI = "/api/ai";

/** STEP 4 AI Growth Agent API client */
export const agentService = {
  analyzeGoal(goalId: number): Promise<GoalAnalysis> {
    return apiRequest(`${AI}/goal/${goalId}/analyze`, { method: "POST", auth: true });
  },

  generatePlan(goalId: number): Promise<GeneratePlanResult> {
    return apiRequest(`${AI}/planner/${goalId}/generate`, { method: "POST", auth: true });
  },

  getGrowthDNA(): Promise<GrowthDNAProfile> {
    return apiRequest(`${AI}/growth-dna`, { auth: true });
  },

  analyzeFailure(missionId: number, notes?: string, autoReplan = false): Promise<FailureRecovery> {
    const qs = autoReplan ? "?auto_replan=true" : "";
    return apiRequest(`${AI}/failure/${missionId}/analyze${qs}`, {
      method: "POST",
      body: notes ? { notes } : {},
      auth: true,
    });
  },

  autoReplan(goalId: number): Promise<AutoReplanResult> {
    return apiRequest(`${AI}/replanner/${goalId}`, { method: "POST", auth: true });
  },

  predictGrowth(goalId: number): Promise<GrowthPredictor> {
    return apiRequest(`${AI}/predictor/${goalId}`, { method: "POST", auth: true });
  },

  simulateFuture(goalId: number): Promise<FutureSimulation> {
    return apiRequest(`${AI}/simulation/${goalId}`, { method: "POST", auth: true });
  },

  listTimeline(): Promise<TimelineEvent[]> {
    return apiRequest(`${AI}/timeline`, { auth: true });
  },

  getGrowthStory(): Promise<GrowthStory> {
    return apiRequest(`${AI}/timeline/story`, { auth: true });
  },

  getRecommendations(): Promise<Recommendations> {
    return apiRequest(`${AI}/recommendations`, { auth: true });
  },

  coachFeedback(context: string): Promise<CoachFeedback> {
    return apiRequest(`${AI}/coach/feedback`, {
      method: "POST",
      body: { context },
      auth: true,
    });
  },

  getPersonality(): Promise<PersonalityInfo> {
    return apiRequest(`${AI}/personality`, { auth: true });
  },

  updatePersonality(personality: string): Promise<PersonalityInfo> {
    return apiRequest(`${AI}/personality`, {
      method: "PUT",
      body: { personality },
      auth: true,
    });
  },
};
