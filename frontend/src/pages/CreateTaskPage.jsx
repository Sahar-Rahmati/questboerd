import DashboardLayout from "../components/layout/DashboardLayout";
import { Link } from "react-router-dom";

export default function CreateTaskPage() {
  return (
    <DashboardLayout>
      <div className="panel max-w-3xl p-8">
        <div>
          <h2 className="text-3xl font-bold text-brand-ink">Create Task</h2>
          <p className="mt-2 text-sm text-slate-600">
            Task creation now happens directly on the dashboard so you can add a task, see the AI estimate, and manage today’s work in one place.
          </p>
        </div>
        <Link
          to="/"
          className="mt-6 inline-flex rounded-2xl bg-brand-lagoon px-5 py-3 text-sm font-semibold text-white transition hover:bg-brand-ink"
        >
          Go to dashboard planner
        </Link>
      </div>
    </DashboardLayout>
  );
}
