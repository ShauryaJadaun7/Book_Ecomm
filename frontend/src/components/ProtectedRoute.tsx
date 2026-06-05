import { useEffect, useState } from "react";
import { useNavigate, Outlet } from "react-router-dom";

export default function ProtectedRoute() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/me");
        if (!res.ok) {
          navigate("/login");
          return;
        }
        // Authentication succeeded
      } catch (err) {
        console.log(err);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };
    checkAuth();
  }, [navigate]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-900">
        <div className="font-mono text-primary font-black animate-pulse text-2xl uppercase tracking-widest">
          Authenticating...
        </div>
      </div>
    );
  }

  return <Outlet />;
}
