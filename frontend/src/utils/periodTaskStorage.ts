const PREFIX = "growthpilot_period_done_";

export function isLocalPeriodTaskDone(taskId: string): boolean {
  return localStorage.getItem(`${PREFIX}${taskId}`) === "1";
}

export function setLocalPeriodTaskDone(taskId: string, done: boolean): void {
  if (done) {
    localStorage.setItem(`${PREFIX}${taskId}`, "1");
  } else {
    localStorage.removeItem(`${PREFIX}${taskId}`);
  }
}
