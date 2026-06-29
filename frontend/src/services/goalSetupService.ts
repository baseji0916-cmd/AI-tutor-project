import { agentService } from "@/services/agentService";
import { goalService } from "@/services/goalService";
import type {
  CoachFeedback,
  GeneratePlanResult,
  Goal,
  GoalAnalysis,
  GoalCreateRequest,
} from "@/types";

export interface GoalSetupResult {
  goal: Goal;
  analysis: GoalAnalysis;
  plan: GeneratePlanResult;
  coach: CoachFeedback;
}

/** Create a goal and run the full GPT agent pipeline (analyze → plan → coach). */
export async function setupGoalWithAI(
  payload: GoalCreateRequest,
  originalText: string,
  onProgress?: (message: string) => void,
): Promise<GoalSetupResult> {
  onProgress?.("목표를 저장하고 있어요…");
  const goal = await goalService.create(payload);

  onProgress?.("GPT가 목표를 분석하고 있어요…");
  const analysis = await agentService.analyzeGoal(goal.id);

  onProgress?.("일·주·월간 계획과 오늘의 미션을 생성하고 있어요…");
  const plan = await agentService.generatePlan(goal.id);

  onProgress?.("AI 코치 조언을 준비하고 있어요…");
  const coach = await agentService.coachFeedback(
    `새로 설정한 목표: ${goal.title}. 사용자 입력: ${originalText}. ` +
      `현실성 점수 ${analysis.realism_score}점. 세부 목표 ${analysis.sub_goals.length}개.`,
  );

  return { goal, analysis, plan, coach };
}

export function formatSetupSummary(result: GoalSetupResult): string {
  const { goal, analysis, plan, coach } = result;

  const planLines = plan.plans.map((p) => {
    const label =
      p.plan_type === "monthly"
        ? "월간"
        : p.plan_type === "weekly"
          ? "주간"
          : p.plan_type === "daily"
            ? "일간"
            : p.plan_type;
    return `• ${label}: ${p.title}`;
  });

  const subGoalLines = analysis.sub_goals.slice(0, 3).map((sg) => `  - ${sg.title}`);
  const missionPreview = plan.missions
    .slice(0, 3)
    .map((m) => `  - ${m.title}`)
    .join("\n");

  return [
    `「${goal.title}」 목표가 등록됐어요! (${goal.end_date}까지)`,
    "",
    `📊 GPT 분석 — 현실성 ${analysis.realism_score}점`,
    analysis.realism_analysis,
    subGoalLines.length ? "\n세부 목표:\n" + subGoalLines.join("\n") : "",
    planLines.length ? "\n📅 계획 수립:\n" + planLines.join("\n") : "",
    plan.missions.length
      ? `\n✅ 오늘부터 ${plan.missions.length}개 미션이 생성됐어요:\n${missionPreview}`
      : "",
    analysis.recommendations?.length
      ? `\n💡 추천: ${analysis.recommendations.slice(0, 2).join(" · ")}`
      : "",
    `\n🎯 AI 코치: ${coach.message}`,
    coach.action_items.length
      ? "\n다음 행동:\n" + coach.action_items.map((a) => `→ ${a}`).join("\n")
      : "",
  ]
    .filter(Boolean)
    .join("\n");
}
