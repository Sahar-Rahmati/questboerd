import Navbar from "./Navbar";
import Sidebar from "./Sidebar";

export default function DashboardLayout({ children }) {
  return (
    <div className="mx-auto grid min-h-screen max-w-7xl gap-6 px-4 py-4 lg:grid-cols-[280px_1fr]">
      <Sidebar />
      <div className="space-y-6">
        <Navbar />
        <main>{children}</main>
      </div>
    </div>
  );
}
