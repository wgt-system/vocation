export function Loading({ label = "Wird geladen …" }: { label?: string }) {
  return (
    <p className="state" role="status">
      {label}
    </p>
  );
}

export function ErrorState({ message }: { message: string }) {
  return (
    <p className="state state-error" role="alert">
      {message}
    </p>
  );
}

export function EmptyState({ children }: { children: React.ReactNode }) {
  return <div className="empty-state">{children}</div>;
}
