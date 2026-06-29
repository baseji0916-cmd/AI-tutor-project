import { useState } from "react";
import { Link } from "react-router-dom";
import { GoalCard } from "@/components/features/goals/GoalCard";
import { GoalFormModal } from "@/components/features/goals/GoalFormModal";
import { Button } from "@/components/ui/Button";
import { PageHeader } from "@/components/ui/PageHeader";
import { Spinner } from "@/components/ui/Spinner";
import { useGoals } from "@/hooks/useGoals";
import { ApiClientError } from "@/services/api";
import { goalService } from "@/services/goalService";
import type { Goal, GoalCreateRequest, GoalStatus } from "@/types";

export function GoalsPage() {
  const { goals, isLoading, error, refetch } = useGoals();
  const [modalOpen, setModalOpen] = useState(false);
  const [editingGoal, setEditingGoal] = useState<Goal | null>(null);

  const handleCreate = () => {
    setEditingGoal(null);
    setModalOpen(true);
  };

  const handleEdit = (goal: Goal) => {
    setEditingGoal(goal);
    setModalOpen(true);
  };

  const handleSubmit = async (
    data: GoalCreateRequest & { status?: GoalStatus },
  ) => {
    try {
      if (editingGoal) {
        await goalService.update(editingGoal.id, data);
      } else {
        await goalService.create(data);
      }
      await refetch();
    } catch (err) {
      throw new Error(
        err instanceof ApiClientError ? err.message : "저장에 실패했습니다.",
      );
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm("이 목표를 삭제할까요?")) return;
    try {
      await goalService.delete(id);
      await refetch();
    } catch (err) {
      alert(err instanceof ApiClientError ? err.message : "삭제에 실패했습니다.");
    }
  };

  const handleStatusChange = async (id: number, status: GoalStatus) => {
    try {
      await goalService.update(id, { status });
      await refetch();
    } catch (err) {
      alert(err instanceof ApiClientError ? err.message : "상태 변경에 실패했습니다.");
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <PageHeader
        title="목표 관리"
        subtitle="목표 CRUD · AI 기능은 AI 계획 / Simulation 메뉴에서"
        action={<Button onClick={handleCreate}>+ 새 목표</Button>}
      />

      <div className="flex flex-wrap gap-2 text-sm">
        <Link
          to="/ai-plan"
          className="px-3 py-1.5 rounded-full bg-accent/10 text-accent font-medium"
        >
          AI 계획 →
        </Link>
        <Link
          to="/simulation"
          className="px-3 py-1.5 rounded-full bg-surface-muted text-text-muted font-medium"
        >
          Future Simulation →
        </Link>
      </div>

      {error ? (
        <div className="rounded-2xl bg-red-500/10 border border-red-500/20 px-4 py-3 text-sm text-red-500">
          {error}
        </div>
      ) : null}

      {isLoading ? (
        <div className="flex justify-center py-20">
          <Spinner />
        </div>
      ) : goals.length === 0 ? (
        <div className="text-center py-20 space-y-4 rounded-2xl border border-border/60 bg-surface-elevated">
          <span className="text-5xl opacity-60">◎</span>
          <p className="text-text-muted">아직 등록된 목표가 없습니다</p>
          <Button onClick={handleCreate}>첫 목표 만들기</Button>
        </div>
      ) : (
        <div className="grid gap-4 sm:grid-cols-2">
          {goals.map((goal) => (
            <GoalCard
              key={goal.id}
              goal={goal}
              onEdit={handleEdit}
              onDelete={handleDelete}
              onStatusChange={handleStatusChange}
            />
          ))}
        </div>
      )}

      <GoalFormModal
        open={modalOpen}
        goal={editingGoal}
        onClose={() => setModalOpen(false)}
        onSubmit={handleSubmit}
      />
    </div>
  );
}
