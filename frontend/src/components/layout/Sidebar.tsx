import { NavLink } from "react-router-dom";
import { mainNavItems } from "@/config/navigation";
import { cn } from "@/utils/cn";

export function Sidebar() {
  return (
    <aside className="hidden lg:flex w-[260px] flex-col border-r border-border/60 bg-surface-elevated/80 backdrop-blur-2xl">
      <div className="flex h-[52px] items-center px-5">
        <span className="text-[17px] font-semibold tracking-tight text-text">
          Growth<span className="text-accent">Pilot</span>
        </span>
      </div>
      <nav className="flex-1 px-3 py-2 space-y-0.5 overflow-y-auto">
        {mainNavItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 px-3 py-2 rounded-xl text-[13px] font-medium transition-all duration-200",
                isActive
                  ? "bg-accent/12 text-accent"
                  : "text-text-muted hover:text-text hover:bg-surface-muted/80",
              )
            }
          >
            <span className="w-5 text-center text-[15px] opacity-80" aria-hidden>
              {item.icon}
            </span>
            <span>{item.label}</span>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}

export { mainNavItems as navItems };
