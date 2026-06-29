import { agentService } from "@/services/agentService";
import { formatSetupSummary, setupGoalWithAI } from "@/services/goalSetupService";
import type { CoachFeedback } from "@/types";
import { isGoalIntent } from "@/utils/detectMessageIntent";
import { parseGoalFromText } from "@/utils/parseGoalInput";

export type CoachMessageResult = {
  mode: "goal" | "coach";
  reply: string;
  goalCreated: boolean;
};

export function formatCoachReply(feedback: CoachFeedback): string {
  const lines = [feedback.message];
  if (feedback.action_items.length > 0) {
    lines.push("", "다음 행동:");
    feedback.action_items.forEach((a) => lines.push(`→ ${a}`));
  }
  return lines.join("\n");
}

/** Route user message to goal setup pipeline or coach feedback. */
export async function handleAICoachMessage(
  text: string,
  onProgress?: (message: string) => void,
): Promise<CoachMessageResult> {
  if (isGoalIntent(text)) {
    const payload = parseGoalFromText(text);
    const result = await setupGoalWithAI(payload, text, onProgress);
    return {
      mode: "goal",
      reply: formatSetupSummary(result),
      goalCreated: true,
    };
  }

  onProgress?.("AI 코치가 답변을 준비하고 있어요…");
  const coach = await agentService.coachFeedback(text);
  return {
    mode: "coach",
    reply: formatCoachReply(coach),
    goalCreated: false,
  };
}

export const AI_COACH_WELCOME =
  "안녕하세요! 저는 당신의 AI 성장 코치예요.\n\n" +
  "• 새 목표를 말씀해 주시면 → GPT 분석 · 월·주·일 계획 · 오늘의 미션까지 만들어 드려요\n" +
  "• 고민·진행 상황·기분을 말씀해 주시면 → 맞춤 코칭을 드려요\n\n" +
  '예: "3개월 안에 토익 900점 달성하고 싶어" / "오늘 의욕이 안 나요"';
