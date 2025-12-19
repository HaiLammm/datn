import { getSession, getDefaultRedirect, getRoleDisplayName } from "@/lib/auth";
import { UnauthorizedContent } from "./UnauthorizedContent";

export default async function UnauthorizedPage() {
  const session = await getSession();
  
  // Determine where to redirect the user
  const homeLink = session 
    ? getDefaultRedirect(session.user.role)
    : "/login";
  
  const homeLinkText = session
    ? `Go to ${getRoleDisplayName(session.user.role)} Dashboard`
    : "Go to Login";

  const roleDisplayName = session 
    ? getRoleDisplayName(session.user.role)
    : null;

  return (
    <UnauthorizedContent 
      homeLink={homeLink}
      homeLinkText={homeLinkText}
      roleDisplayName={roleDisplayName}
    />
  );
}
