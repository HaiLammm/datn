import { Shield, Users, FileText, Briefcase } from "lucide-react";
import Link from "next/link";

export default async function AdminPage() {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Admin Dashboard</h1>
        <p className="text-gray-600">
          System overview and management tools.
        </p>
      </div>

      {/* Quick Stats Cards */}
      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">Total Users</h3>
            <Users className="h-5 w-5 text-blue-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">-</p>
          <p className="text-xs text-gray-500 mt-1">Fetched from API</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">Total CVs</h3>
            <FileText className="h-5 w-5 text-green-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">-</p>
          <p className="text-xs text-gray-500 mt-1">Fetched from API</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">Total JDs</h3>
            <Briefcase className="h-5 w-5 text-purple-500" />
          </div>
          <p className="text-2xl font-bold text-gray-900">-</p>
          <p className="text-xs text-gray-500 mt-1">Fetched from API</p>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-medium text-gray-500">System Status</h3>
            <Shield className="h-5 w-5 text-orange-500" />
          </div>
          <p className="text-2xl font-bold text-green-600">Healthy</p>
          <p className="text-xs text-gray-500 mt-1">All systems operational</p>
        </div>
      </div>

      {/* Quick Links */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid gap-4 md:grid-cols-3">
          <Link
            href="/admin/users"
            className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <Users className="h-8 w-8 text-blue-500" />
            <div>
              <p className="font-medium text-gray-900">Manage Users</p>
              <p className="text-sm text-gray-500">View and manage user accounts</p>
            </div>
          </Link>
          
          <Link
            href="/cvs"
            className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <FileText className="h-8 w-8 text-green-500" />
            <div>
              <p className="font-medium text-gray-900">View CVs</p>
              <p className="text-sm text-gray-500">Browse all uploaded CVs</p>
            </div>
          </Link>
          
          <Link
            href="/jobs"
            className="flex items-center gap-3 p-4 rounded-lg border border-gray-200 hover:bg-gray-50 transition-colors"
          >
            <Briefcase className="h-8 w-8 text-purple-500" />
            <div>
              <p className="font-medium text-gray-900">View Jobs</p>
              <p className="text-sm text-gray-500">Browse all job descriptions</p>
            </div>
          </Link>
        </div>
      </div>
    </div>
  );
}
