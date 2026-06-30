/** AI coach personality — mirrors backend CoachPersonality enum */
export type CoachPersonality =
  | "teacher"
  | "friend"
  | "passion"
  | "data_analyst"
  | "ceo"
  | "tsundere";

export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string | null;
  bio: string | null;
  coach_personality: CoachPersonality;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
  coach_personality?: CoachPersonality;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface ApiError {
  detail: string | { msg: string; type: string }[];
}

export type GoalStatus = "active" | "completed" | "paused" | "abandoned";

export interface Goal {
  id: number;
  user_id: number;
  title: string;
  description: string | null;
  priority: number;
  status: GoalStatus;
  start_date: string;
  end_date: string;
  progress_rate: number;
  created_at: string;
  updated_at: string;
}

export interface GoalCreateRequest {
  title: string;
  description?: string;
  priority: number;
  start_date: string;
  end_date: string;
}

export interface GoalUpdateRequest {
  title?: string;
  description?: string;
  priority?: number;
  status?: GoalStatus;
  start_date?: string;
  end_date?: string;
}

export interface DashboardStats {
  progress_rate: number;
  achievement_rate: number;
  growth_score: number;
  today_missions_total: number;
  today_missions_completed: number;
  active_goals: number;
}

export type PeriodHorizon = "daily" | "weekly" | "monthly";

export type PeriodTaskSource = "mission" | "plan" | "template" | "goal";

export interface PeriodTaskItem {
  id: string;
  title: string;
  description?: string | null;
  goal_id?: number | null;
  goal_title?: string | null;
  status: MissionStatus | "pending" | "completed" | "failed";
  source: PeriodTaskSource;
  mission_id?: number | null;
  scheduled_date?: string | null;
}

export interface PeriodSection {
  horizon: PeriodHorizon;
  label: string;
  period_label: string;
  total: number;
  completed: number;
  progress_rate: number;
  is_template: boolean;
  items: PeriodTaskItem[];
}

export interface PeriodGoalSummary {
  id: number;
  title: string;
  description?: string | null;
  progress_rate: number;
  status: GoalStatus;
  end_date: string;
}

export interface PeriodRoadmap {
  overall_goals: PeriodGoalSummary[];
  daily: PeriodSection;
  weekly: PeriodSection;
  monthly: PeriodSection;
}

export const GOAL_STATUS_LABELS: Record<GoalStatus, string> = {
  active: "진행 중",
  completed: "완료",
  paused: "일시정지",
  abandoned: "포기",
};

export const PRIORITY_LABELS: Record<number, string> = {
  1: "최우선",
  2: "높음",
  3: "보통",
  4: "낮음",
  5: "최하",
};

export type MissionStatus = "pending" | "completed" | "failed" | "skipped";

export interface Mission {
  id: number;
  goal_id: number;
  goal_title: string;
  title: string;
  description: string | null;
  scheduled_date: string;
  status: MissionStatus;
  completed_at?: string | null;
}

export interface TimelineEvent {
  id: number;
  event_type: string;
  title: string;
  description: string | null;
  occurred_at: string;
}

export interface SubGoal {
  title: string;
  description: string;
}

export interface GoalAnalysis {
  goal_id: number;
  realism_score: number;
  realism_analysis: string;
  sub_goals: SubGoal[];
  recommendations: string[];
  risks: string[];
  llm_mode: string;
}

export interface GeneratePlanResult {
  goal_id: number;
  realism_score: number;
  realism_analysis: string;
  sub_goals: SubGoal[];
  recommendations: string[];
  plans: { id: number; plan_type: string; title: string; content: string | null }[];
  missions: { id: number; title: string; status: string }[];
  memory_insight: string;
  updated_growth_score: number;
  llm_mode: string;
}

export interface FailureAnalysis {
  mission_id: number;
  root_causes: string[];
  patterns: string[];
  improvements: string[];
  summary: string;
  llm_mode: string;
}

export interface FailureRecovery extends FailureAnalysis {
  dna_updated: boolean;
  replanned: boolean;
  replan: AutoReplanResult | null;
}

export interface AutoReplanResult {
  goal_id: number;
  revision_summary: string;
  plans: { id: number; plan_type: string; title: string; content: string | null }[];
  missions: { id: number; title: string; status: string }[];
  memory_insight: string;
  updated_growth_score: number;
  llm_mode: string;
}

export interface GrowthDNAProfile {
  focus_time: number;
  success_patterns: string[];
  failure_patterns: string[];
  preferred_feedback_style: string | null;
  growth_score: number;
  llm_mode: string;
}

export interface GrowthPredictor {
  goal_id: number;
  achievement_probability: number;
  confidence_level: string;
  key_factors: string[];
  recommendations: string[];
  predicted_completion_date: string;
  llm_mode: string;
}

export interface PersonalityOption {
  id: string;
  label_ko: string;
  description: string;
}

export interface PersonalityInfo {
  current: CoachPersonality;
  label_ko: string;
  available: PersonalityOption[];
}

export interface CoachFeedback {
  message: string;
  action_items: string[];
  tone: string;
  llm_mode: string;
}

export interface Recommendations {
  goals: string[];
  books: string[];
  skills: string[];
  habits: string[];
  llm_mode: string;
}

export interface FutureScenario {
  name: string;
  description: string;
  achievement_probability: number;
  expected_completion_date: string;
  required_effort_hours: number;
}

export interface FutureSimulation {
  goal_id: number;
  achievement_probability: number;
  expected_completion_date: string;
  required_effort_hours: number;
  scenarios: FutureScenario[];
  llm_mode: string;
}

export interface GrowthStory {
  story: string;
  highlights: string[];
  llm_mode: string;
}

export const MISSION_STATUS_LABELS: Record<MissionStatus, string> = {
  pending: "대기",
  completed: "완료",
  failed: "실패",
  skipped: "건너뜀",
};

/** Display labels for coach personality selector */
export const COACH_PERSONALITY_OPTIONS: {
  value: CoachPersonality;
  label: string;
  description: string;
}[] = [
  { value: "teacher", label: "선생님형", description: "체계적 단계별 코칭" },
  { value: "friend", label: "친구형", description: "편안한 격려와 공감" },
  { value: "passion", label: "열정 코치형", description: "에너지 넘치는 동기부여" },
  { value: "data_analyst", label: "데이터 분석형", description: "수치 기반 피드백" },
  { value: "ceo", label: "CEO형", description: "전략적 결과 중심" },
  { value: "tsundere", label: "츤데레형", description: "까칠하지만 진심 어린 코칭" },
];
