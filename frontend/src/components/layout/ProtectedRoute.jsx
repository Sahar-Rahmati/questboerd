import { Navigate, Outlet, useLocation } from "react-router-dom";
import LoadingSpinner from "../common/LoadingSpinner";
import { useAuth } from "../../hooks/useAuth";

export default function ProtectedRoute() {
  const { user, loading } = useAuth();
  const location = useLocation();

  if (loading) {
    return <LoadingSpinner label="Restoring your session..." />;
  }

  if (!user) {
    return <Navigate to="/login" replace state={{ from: location }} />;
  }

  return <Outlet />;
}
