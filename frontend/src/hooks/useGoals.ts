import { useCallback, useEffect, useState } from "react";
import { goalService } from "@/services/goalService";
import { ApiClientError } from "@/services/api";
import type { Goal } from "@/types";

export function useGoals() {
  const [goals, setGoals] = useState<Goal[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchGoals = useCallback(async () => {
    setIsLoading(true);
    setError("");
    try {
      const data = await goalService.list();
      setGoals(data);
    } catch (err) {
      setError(
        err instanceof ApiClientError ? err.message : "목표를 불러오지 못했습니다.",
      );
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    void fetchGoals();
  }, [fetchGoals]);

  return { goals, isLoading, error, refetch: fetchGoals };
}
