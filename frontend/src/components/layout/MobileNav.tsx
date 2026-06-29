import { NavLink, useLocation } from "react-router-dom";
import { mobileMoreNav, mobilePrimaryNav } from "@/config/navigation";
import { cn } from "@/utils/cn";

/** Bottom tab bar — primary screens + More */
export function MobileNav() {
  const location = useLocation();
  const moreActive =
    location.pathname === "/more" ||
    mobileMoreNav.some((i) => location.pathname.startsWith(i.to));

  return (
    <nav className="lg:hidden fixed bottom-0 inset-x-0 z-50 border-t border-border/60 bg-surface-elevated/90 backdrop-blur-2xl pb-[env(safe-area-inset-bottom)]">
      <div className="flex items-stretch justify-around h-[52px] px-1">
        {mobilePrimaryNav.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex flex-col items-center justify-center flex-1 gap-0.5 text-[10px] font-medium transition-colors min-w-0",
                isActive ? "text-accent" : "text-text-muted",
              )
            }
          >
            <span className="text-[18px] leading-none" aria-hidden>
              {item.icon}
            </span>
            <span className="truncate max-w-full px-0.5">{item.label.split(" ")[0]}</span>
          </NavLink>
        ))}
        <NavLink
          to="/more"
          className={cn(
            "flex flex-col items-center justify-center flex-1 gap-0.5 text-[10px] font-medium transition-colors",
            moreActive ? "text-accent" : "text-text-muted",
          )}
        >
          <span className="text-[18px] leading-none" aria-hidden>
            ···
          </span>
          <span>더보기</span>
        </NavLink>
      </div>
    </nav>
  );
}
