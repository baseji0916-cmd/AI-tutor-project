/** Detect whether the user wants to set a goal vs. general coaching chat. */
export function isGoalIntent(text: string): boolean {
  const t = text.trim();
  if (t.length < 4) return false;

  const goalPatterns = [
    /목표/i,
    /하고\s*싶/i,
    /싶어/i,
    /달성/i,
    /이루/i,
    /마스터/i,
    /배우/i,
    /익히/i,
    /준비/i,
    /(\d+)\s*(개월|주|일|년)/,
    /계획\s*(세|잡|만들|짜)/,
    /새\s*목표/,
    /목표\s*(설|잡|등)/,
    /토익|토플|자격|시험|합격|감량|운동|다이어트|영어|코딩|개발/,
  ];

  const coachOnlyPatterns = [
    /^오늘\s*(기분|컨디션)/,
    /힘들|지치|우울|불안|의욕/,
    /조언|팁|어떻게\s*하면/,
    /왜\s*.+\?/,
    /고민/,
    /응원/,
    /칭찬/,
  ];

  if (coachOnlyPatterns.some((p) => p.test(t)) && !goalPatterns.slice(0, 10).some((p) => p.test(t))) {
    return false;
  }

  return goalPatterns.some((p) => p.test(t));
}
