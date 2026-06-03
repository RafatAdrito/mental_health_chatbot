import { LogOutIcon, MenuIcon, SmilePlusIcon, UserIcon } from "lucide-react";
import { HeartPulseIcon } from "lucide-react";
import useStore from "../store";

export function Header({ onMenuClick }) {
  const isConnected = useStore((s) => s.isConnected);
  const setShowMoodCheckin = useStore((s) => s.setShowMoodCheckin);
  const currentUser = useStore((s) => s.currentUser);
  const logout = useStore((s) => s.logout);

  return (
    <header className="sticky top-0 z-10 flex flex-shrink-0 items-center justify-between gap-2 border-b border-zinc-800 bg-zinc-950/90 px-3 py-3 backdrop-blur-sm sm:px-5 sm:py-3.5">
      <div className="flex min-w-0 items-center gap-2 sm:gap-2.5">
        <button
          onClick={onMenuClick}
          className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-lg border border-zinc-700/80 text-zinc-400 transition-colors hover:border-zinc-500 hover:text-zinc-100 md:hidden"
          aria-label="Open conversation history"
        >
          <MenuIcon size={15} />
        </button>
        <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-600/20 border border-indigo-500/40">
          <HeartPulseIcon size={15} className="text-indigo-400" />
        </div>
        <span className="truncate text-sm font-semibold tracking-tight text-zinc-100">
          MindfulChat
        </span>
        <span
          className={`w-1.5 h-1.5 rounded-full ml-1 transition-colors ${
            isConnected ? "bg-emerald-500" : "bg-zinc-600"
          }`}
        />
      </div>

      <div className="flex flex-shrink-0 items-center gap-1.5 sm:gap-2">
        <button
          onClick={() => setShowMoodCheckin(true)}
          className="flex h-8 items-center gap-1.5 rounded-lg border border-zinc-700/80 px-2.5 text-xs text-zinc-400 transition-all duration-150 hover:border-zinc-500 hover:bg-zinc-800/50 hover:text-zinc-100 active:scale-95 sm:px-3"
          aria-label="Log mood"
        >
          <SmilePlusIcon size={13} />
          <span className="hidden sm:inline">Log Mood</span>
        </button>

        {/* User profile chip */}
        {currentUser && (
          <div className="hidden h-8 max-w-[8rem] items-center gap-1.5 rounded-lg border border-zinc-700/80 px-2.5 text-xs text-zinc-400 min-[420px]:flex sm:max-w-[10rem] sm:px-3">
            <UserIcon size={12} className="text-indigo-400" />
            <span className="text-zinc-300 max-w-[80px] truncate">
              {currentUser.display_name || currentUser.username}
            </span>
          </div>
        )}

        <button
          onClick={logout}
          title="Sign out"
          className="flex h-8 items-center gap-1.5 rounded-lg border border-zinc-700/80 px-2.5 text-xs text-zinc-400 transition-all duration-150 hover:border-red-800/60 hover:bg-red-950/20 hover:text-red-400 active:scale-95 sm:px-3"
          aria-label="Sign out"
        >
          <LogOutIcon size={13} />
          <span className="hidden sm:inline">Sign Out</span>
        </button>
      </div>
    </header>
  );
}
