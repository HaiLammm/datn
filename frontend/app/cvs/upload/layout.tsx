// This layout is now a simple pass-through component.
// The authentication guard has been moved to page.tsx to avoid
// interfering with Server Action POST requests.
export default function CVUploadLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return <>{children}</>;
}