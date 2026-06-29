import { FormEvent, useCallback, useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Card } from "@/components/ui/Card";
import { useSpeechRecognition } from "@/hooks/useSpeechRecognition";
import { ApiClientError } from "@/services/api";
import {
  AI_COACH_WELCOME,
  handleAICoachMessage,
} from "@/services/aiCoachService";
import { agentService } from "@/services/agentService";
import type { Recommendations } from "@/types";
import { cn } from "@/utils/cn";

interface ChatMessage {
  role: "user" | "assistant";
  text: string;
}

interface AICoachChatProps {
  onGoalCreated?: () => void;
  variant?: "compact" | "full";
  showRecommendations?: boolean;
}

export function AICoachChat({
  onGoalCreated,
  variant = "compact",
  showRecommendations = false,
}: AICoachChatProps) {
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([
    { role: "assistant", text: AI_COACH_WELCOME },
  ]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [statusText, setStatusText] = useState("");
  const [recommendations, setRecommendations] = useState<Recommendations | null>(null);

  useEffect(() => {
    if (showRecommendations) {
      agentService.getRecommendations().then(setRecommendations).catch(() => null);
    }
  }, [showRecommendations]);

  const appendVoice = useCallback((text: string) => {
    setInput((prev) => (prev ? `${prev} ${text}` : text));
  }, []);

  const { isListening, isSupported, startListening, stopListening } =
    useSpeechRecognition(appendVoice);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    const text = input.trim();
    if (!text || isSubmitting) return;

    setMessages((prev) => [...prev, { role: "user", text }]);
    setInput("");
    setIsSubmitting(true);

    try {
      const result = await handleAICoachMessage(text, setStatusText);
      setStatusText("");
      setMessages((prev) => [...prev, { role: "assistant", text: result.reply }]);
      if (result.goalCreated) onGoalCreated?.();
    } catch (err) {
      setStatusText("");
      const detail =
        err instanceof ApiClientError
          ? err.message
          : err instanceof Error
            ? err.message
            : "알 수 없는 오류";
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          text: `답변에 실패했어요: ${detail}\n\n잠시 후 다시 시도해 주세요.`,
        },
      ]);
    } finally {
      setIsSubmitting(false);
    }
  };

  const toggleVoice = () => {
    if (isListening) stopListening();
    else startListening();
  };

  const chatHeight = variant === "full" ? "max-h-[min(60vh,520px)]" : "max-h-72";

  return (
    <div className="space-y-4">
      <Card
        title="AI 코치"
        subtitle="목표 설정 · 계획 수립 · 코칭 — 하나의 대화로"
      >
        <div className={cn("space-y-3 overflow-y-auto pr-1 mb-4", chatHeight)}>
          {messages.map((msg, i) => (
            <div
              key={`${msg.role}-${i}`}
              className={cn(
                "rounded-2xl px-4 py-2.5 text-sm leading-relaxed whitespace-pre-wrap",
                msg.role === "user"
                  ? "ml-auto bg-accent text-white max-w-[85%]"
                  : "mr-auto bg-surface-muted text-text max-w-[95%]",
              )}
            >
              {msg.text}
            </div>
          ))}
          {statusText ? (
            <p className="text-xs text-accent text-center animate-pulse">{statusText}</p>
          ) : null}
        </div>

        <form onSubmit={handleSubmit} className="flex gap-2">
          <input
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="목표, 고민, 진행 상황… (🎤 음성 가능)"
            className="flex-1 h-11 px-4 rounded-xl bg-surface-muted border border-border/60 text-[15px] text-text placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent/30"
            disabled={isSubmitting}
          />
          {isSupported ? (
            <Button
              type="button"
              variant={isListening ? "danger" : "secondary"}
              size="md"
              onClick={toggleVoice}
              disabled={isSubmitting}
              aria-label={isListening ? "음성 입력 중지" : "음성 입력 시작"}
              className="!px-3 shrink-0"
            >
              {isListening ? "⏹" : "🎤"}
            </Button>
          ) : null}
          <Button type="submit" isLoading={isSubmitting} className="shrink-0">
            전송
          </Button>
        </form>

        {!isSupported ? (
          <p className="text-[11px] text-text-muted mt-2">
            이 브라우저는 음성 입력을 지원하지 않습니다.
          </p>
        ) : isListening ? (
          <p className="text-[11px] text-accent mt-2 animate-pulse">듣고 있어요…</p>
        ) : null}
      </Card>

      {showRecommendations && recommendations ? (
        <Card title="Smart Recommendation">
          <div className="grid sm:grid-cols-2 gap-4 text-sm">
            {(
              [
                ["추천 목표", recommendations.goals],
                ["추천 도서", recommendations.books],
                ["추천 역량", recommendations.skills],
                ["추천 습관", recommendations.habits],
              ] as const
            ).map(([label, items]) => (
              <div key={label}>
                <p className="text-xs font-medium text-text-muted uppercase tracking-wide mb-2">
                  {label}
                </p>
                <ul className="space-y-1 text-text">
                  {items.map((item) => (
                    <li
                      key={item}
                      className="rounded-lg bg-surface-muted/50 px-3 py-2 text-[13px]"
                    >
                      {item}
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        </Card>
      ) : null}
    </div>
  );
}
