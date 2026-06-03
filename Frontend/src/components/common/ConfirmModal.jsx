export function ConfirmModal({
  isOpen,
  title,
  message,
  onConfirm,
  onCancel,
  isLoading,
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-4">
      {/* Backdrop */}
      <div
        className="absolute inset-0 bg-black/60 backdrop-blur-sm"
        onClick={!isLoading ? onCancel : undefined}
      />

      {/* Dialog */}
      <div className="relative z-10 w-full max-w-sm rounded-xl border border-zinc-700 bg-zinc-900 p-4 shadow-2xl sm:p-5">
        <h3 className="text-zinc-100 font-semibold text-sm mb-2">{title}</h3>
        <p className="text-zinc-400 text-xs leading-relaxed mb-5">{message}</p>

        <div className="flex flex-col-reverse gap-2 min-[360px]:flex-row min-[360px]:items-center min-[360px]:justify-end">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="px-3 py-1.5 text-xs text-zinc-400 hover:text-zinc-200 border border-zinc-700 hover:border-zinc-500 rounded-lg transition-all disabled:opacity-50"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="flex items-center gap-1.5 px-3 py-1.5 text-xs text-white bg-red-600 hover:bg-red-500 rounded-lg transition-all disabled:opacity-60"
          >
            {isLoading ? (
              <>
                <svg
                  className="animate-spin w-3 h-3"
                  viewBox="0 0 24 24"
                  fill="none"
                >
                  <circle
                    className="opacity-25"
                    cx="12"
                    cy="12"
                    r="10"
                    stroke="currentColor"
                    strokeWidth="4"
                  />
                  <path
                    className="opacity-75"
                    fill="currentColor"
                    d="M4 12a8 8 0 018-8v8H4z"
                  />
                </svg>
                Deleting…
              </>
            ) : (
              "Delete"
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
