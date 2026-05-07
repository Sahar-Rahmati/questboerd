import { Navigate, Route, Routes } from "react-router-dom";
import ProtectedRoute from "../components/layout/ProtectedRoute";
import DashboardPage from "../pages/DashboardPage";
import LeaderboardPage from "../pages/LeaderboardPage";
import LoginPage from "../pages/LoginPage";
import NotFoundPage from "../pages/NotFoundPage";
import ProfilePage from "../pages/ProfilePage";
import RegisterPage from "../pages/RegisterPage";
import RewardsPage from "../pages/RewardsPage";
import WeeklyReportsPage from "../pages/WeeklyReportsPage";

export default function AppRouter() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/register" element={<RegisterPage />} />
      <Route element={<ProtectedRoute />}>
        <Route path="/" element={<DashboardPage />} />
        <Route path="/tasks" element={<Navigate to="/" replace />} />
        <Route path="/tasks/create" element={<Navigate to="/" replace />} />
        <Route path="/activities" element={<Navigate to="/" replace />} />
        <Route path="/rewards" element={<RewardsPage />} />
        <Route path="/leaderboard" element={<LeaderboardPage />} />
        <Route path="/reports" element={<WeeklyReportsPage />} />
        <Route path="/wallet" element={<Navigate to="/rewards" replace />} />
        <Route path="/profile" element={<ProfilePage />} />
      </Route>
      <Route path="*" element={<NotFoundPage />} />
      <Route path="/home" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
