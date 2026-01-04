import Link from "next/link";
import { Upload, FileText, User, MessageSquare } from "lucide-react";
import { Button } from "@/components/ui/button";

export function QuickActions() {
  return (
    <div data-testid="quick-actions">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
      <div className="flex flex-col sm:flex-row gap-4">
        <Button asChild className="flex-1" data-testid="upload-cv-button">
          <Link href="/cvs/upload">
            <Upload className="h-4 w-4 mr-2" />
            Upload New CV
          </Link>
        </Button>
        <Button
          asChild
          variant="outline"
          className="flex-1"
          data-testid="view-history-button"
        >
          <Link href="/cvs">
            <FileText className="h-4 w-4 mr-2" />
            View CV History
          </Link>
        </Button>
        <Button
          asChild
          variant="outline"
          className="flex-1"
          data-testid="messages-button"
        >
          <Link href="/messages">
            <MessageSquare className="h-4 w-4 mr-2" />
            Messages
          </Link>
        </Button>
        <Button
          asChild
          variant="outline"
          className="flex-1"
          data-testid="view-profile-button"
        >
          <Link href="/profile">
            <User className="h-4 w-4 mr-2" />
            My Profile
          </Link>
        </Button>
      </div>
    </div>
  );
}
