/** App navigation — STEP 5 screens */

export interface NavItem {
  to: string;
  label: string;
  icon: string;
  description?: string;
  mobilePrimary?: boolean;
}

export const mainNavItems: NavItem[] = [
  { to: "/dashboard", label: "대시보드", icon: "◉", description: "성장 요약", mobilePrimary: true },
  { to: "/goals", label: "목표", icon: "◎", description: "목표 관리", mobilePrimary: true },
  { to: "/missions", label: "오늘의 미션", icon: "✓", description: "일일 실행", mobilePrimary: true },
  { to: "/ai-plan", label: "AI 계획", icon: "◈", description: "월·주·일 계획" },
  { to: "/progress", label: "진행률", icon: "◐", description: "달성 현황" },
  { to: "/growth-dna", label: "Growth DNA", icon: "◆", description: "성향·패턴" },
  { to: "/simulation", label: "Future Simulation", icon: "◇", description: "시나리오 A/B/C" },
  { to: "/timeline", label: "Growth Timeline", icon: "◔", description: "성장 기록" },
  { to: "/tutor", label: "AI 코치", icon: "◑", description: "목표·코칭 대화", mobilePrimary: true },
  { to: "/settings", label: "설정", icon: "⚙", description: "계정·테마" },
];

export const mobilePrimaryNav = mainNavItems.filter((i) => i.mobilePrimary);
export const mobileMoreNav = mainNavItems.filter((i) => !i.mobilePrimary);
