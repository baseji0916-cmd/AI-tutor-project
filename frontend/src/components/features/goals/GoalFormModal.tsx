import { FormEvent, useEffect, useState } from "react";
import { Button } from "@/components/ui/Button";
import { Input } from "@/components/ui/Input";
import type { Goal, GoalCreateRequest, GoalStatus } from "@/types";
import { GOAL_STATUS_LABELS } from "@/types";

interface GoalFormModalProps {
  open: boolean;
  goal?: Goal | null;
  onClose: () => void;
  onSubmit: (data: GoalCreateRequest & { status?: GoalStatus }) => Promise<void>;
}

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function defaultEndDate() {
  const d = new Date();
  d.setDate(d.getDate() + 90);
  return d.toISOString().slice(0, 10);
}

export function GoalFormModal({ open, goal, onClose, onSubmit }: GoalFormModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState(3);
  const [status, setStatus] = useState<GoalStatus>("active");
  const [startDate, setStartDate] = useState(todayISO());
  const [endDate, setEndDate] = useState(defaultEndDate());
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    if (goal) {
      setTitle(goal.title);
      setDescription(goal.description ?? "");
      setPriority(goal.priority);
      setStatus(goal.status);
      setStartDate(goal.start_date);
      setEndDate(goal.end_date);
    } else {
      setTitle("");
      setDescription("");
      setPriority(3);
      setStatus("active");
      setStartDate(todayISO());
      setEndDate(defaultEndDate());
    }
    setError("");
  }, [goal, open]);

  if (!open) return null;

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      await onSubmit({
        title,
        description: description || undefined,
        priority,
        start_date: startDate,
        end_date: endDate,
        ...(goal ? { status } : {}),
      });
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : "저장에 실패했습니다.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-end sm:items-center justify-center p-4">
      <div
        className="absolute inset-0 bg-black/40 backdrop-blur-sm"
        onClick={onClose}
        aria-hidden
      />
      <div className="relative w-full max-w-lg rounded-2xl border border-border bg-surface-elevated p-6 shadow-xl max-h-[90dvh] overflow-y-auto">
        <h2 className="text-lg font-semibold text-text mb-4">
          {goal ? "목표 수정" : "새 목표 만들기"}
        </h2>

        <form onSubmit={handleSubmit} className="space-y-4">
          {error ? (
            <div className="rounded-xl bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-500">
              {error}
            </div>
          ) : null}

          <Input
            label="목표 제목"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            required
            placeholder="예: 영어 회화 마스터하기"
          />

          <div className="space-y-1.5">
            <label className="block text-sm font-medium text-text">설명 (선택)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              rows={3}
              className="w-full px-4 py-3 rounded-xl bg-surface-muted border border-border text-text placeholder:text-text-muted focus:outline-none focus:ring-2 focus:ring-accent/40 resize-none"
              placeholder="목표에 대한 상세 설명"
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1.5">
              <label className="block text-sm font-medium text-text">우선순위</label>
              <select
                value={priority}
                onChange={(e) => setPriority(Number(e.target.value))}
                className="w-full h-11 px-4 rounded-xl bg-surface-muted border border-border text-text focus:outline-none focus:ring-2 focus:ring-accent/40"
              >
                {[1, 2, 3, 4, 5].map((p) => (
                  <option key={p} value={p}>
                    P{p} {p === 1 ? "(최우선)" : p === 5 ? "(최하)" : ""}
                  </option>
                ))}
              </select>
            </div>

            {goal ? (
              <div className="space-y-1.5">
                <label className="block text-sm font-medium text-text">상태</label>
                <select
                  value={status}
                  onChange={(e) => setStatus(e.target.value as GoalStatus)}
                  className="w-full h-11 px-4 rounded-xl bg-surface-muted border border-border text-text focus:outline-none focus:ring-2 focus:ring-accent/40"
                >
                  {Object.entries(GOAL_STATUS_LABELS).map(([value, label]) => (
                    <option key={value} value={value}>
                      {label}
                    </option>
                  ))}
                </select>
              </div>
            ) : null}
          </div>

          <div className="grid grid-cols-2 gap-4">
            <Input
              label="시작일"
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              required
            />
            <Input
              label="목표일"
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              required
            />
          </div>

          <div className="flex gap-3 pt-2">
            <Button type="button" variant="secondary" className="flex-1" onClick={onClose}>
              취소
            </Button>
            <Button type="submit" className="flex-1" isLoading={isLoading}>
              {goal ? "저장" : "만들기"}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
