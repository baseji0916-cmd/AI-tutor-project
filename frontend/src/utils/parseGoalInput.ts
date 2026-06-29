import type { GoalCreateRequest } from "@/types";

function todayISO() {
  return new Date().toISOString().slice(0, 10);
}

function addDaysISO(days: number) {
  const d = new Date();
  d.setDate(d.getDate() + days);
  return d.toISOString().slice(0, 10);
}

/** Parse conversational Korean/English goal text into a create payload. */
export function parseGoalFromText(text: string): GoalCreateRequest {
  const raw = text.trim();
  let days = 90;
  let priority = 3;

  const monthMatch = raw.match(/(\d+)\s*개월/);
  const weekMatch = raw.match(/(\d+)\s*주/);
  const dayMatch = raw.match(/(\d+)\s*일/);
  const yearMatch = raw.match(/(\d+)\s*년/);

  if (yearMatch) days = parseInt(yearMatch[1], 10) * 365;
  else if (monthMatch) days = parseInt(monthMatch[1], 10) * 30;
  else if (weekMatch) days = parseInt(weekMatch[1], 10) * 7;
  else if (dayMatch) days = parseInt(dayMatch[1], 10);

  if (/중요|급|최우선|꼭/.test(raw)) priority = 1;
  else if (/여유|천천|낮은/.test(raw)) priority = 4;

  let title = raw
    .replace(/^(나는?|저는?|목표는?|내 목표는?)\s*/i, "")
    .replace(/(하고\s*싶(어|습니다|다|어요)|싶어요|목표로\s*삼(을|고)\s*싶(어|습니다|다|어요))\.?\s*$/i, "")
    .replace(/\s*(까지|안에|동안)\s*(\d+\s*(개월|주|일|년)).*$/i, "")
    .trim();

  if (!title || title.length < 2) title = raw;

  return {
    title: title.slice(0, 120),
    description: raw,
    priority,
    start_date: todayISO(),
    end_date: addDaysISO(Math.max(days, 7)),
  };
}
