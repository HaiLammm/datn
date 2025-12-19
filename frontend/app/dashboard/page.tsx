// app/dashboard/page.tsx
import Link from "next/link";
import { redirect } from "next/navigation";
import { FileText, Briefcase, Shield, Upload, Search, Users } from "lucide-react";
import { LogoutButton } from "@/components/auth/LogoutButton";
import { getSession, getRoleDisplayName } from "@/lib/auth";

export default async function DashboardPage() {
  const session = await getSession();
  
  if (!session) {
    redirect("/login");
  }

  const { user } = session;
  const roleDisplayName = getRoleDisplayName(user.role);

  return (
    <main className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Welcome back!
              </h1>
              <p className="text-gray-600 mt-1">
                Logged in as <span className="font-medium">{user.email}</span>
              </p>
              <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 mt-2">
                {roleDisplayName}
              </span>
            </div>
            <LogoutButton />
          </div>
        </div>

        {/* Role-specific content */}
        {user.role === 'job_seeker' && <JobSeekerDashboard />}
        {user.role === 'recruiter' && <RecruiterDashboard />}
        {user.role === 'admin' && <AdminDashboard />}
      </div>
    </main>
  );
}

function JobSeekerDashboard() {
  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Seeker Dashboard</h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <DashboardCard
          href="/cvs"
          icon={<FileText className="h-8 w-8 text-blue-500" />}
          title="My CVs"
          description="View and manage your uploaded CVs"
        />
        <DashboardCard
          href="/cvs/upload"
          icon={<Upload className="h-8 w-8 text-green-500" />}
          title="Upload CV"
          description="Upload a new CV for analysis"
        />
      </div>
    </div>
  );
}

function RecruiterDashboard() {
  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Recruiter Dashboard</h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <DashboardCard
          href="/jobs"
          icon={<Briefcase className="h-8 w-8 text-purple-500" />}
          title="Job Descriptions"
          description="Manage your job postings"
        />
        <DashboardCard
          href="/jobs/jd/upload"
          icon={<Upload className="h-8 w-8 text-green-500" />}
          title="Create JD"
          description="Create a new job description"
        />
        <DashboardCard
          href="/jobs/search"
          icon={<Search className="h-8 w-8 text-orange-500" />}
          title="Search Candidates"
          description="Find matching candidates for your jobs"
        />
      </div>
    </div>
  );
}

function AdminDashboard() {
  return (
    <div>
      <h2 className="text-xl font-semibold text-gray-900 mb-4">Admin Dashboard</h2>
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
        <DashboardCard
          href="/admin"
          icon={<Shield className="h-8 w-8 text-purple-500" />}
          title="Admin Panel"
          description="System overview and management"
        />
        <DashboardCard
          href="/admin/users"
          icon={<Users className="h-8 w-8 text-blue-500" />}
          title="Manage Users"
          description="View and manage user accounts"
        />
        <DashboardCard
          href="/cvs"
          icon={<FileText className="h-8 w-8 text-green-500" />}
          title="All CVs"
          description="Browse all uploaded CVs"
        />
        <DashboardCard
          href="/jobs"
          icon={<Briefcase className="h-8 w-8 text-orange-500" />}
          title="All Jobs"
          description="Browse all job descriptions"
        />
      </div>
    </div>
  );
}

function DashboardCard({
  href,
  icon,
  title,
  description,
}: {
  href: string;
  icon: React.ReactNode;
  title: string;
  description: string;
}) {
  return (
    <Link
      href={href}
      className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
    >
      <div className="flex items-start gap-4">
        {icon}
        <div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
      </div>
    </Link>
  );
}
