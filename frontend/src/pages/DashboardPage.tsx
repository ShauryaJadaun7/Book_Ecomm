import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";

export default function DashboardPage() {
  const navigate = useNavigate();
  const [userData, setUserData] = useState<{name: string, email: string} | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const checkAuth = async () => {
      try {
        const res = await fetch("/api/auth/me");
        if (!res.ok) {
          navigate("/login");
          return;
        }
        const data = await res.json();
        setUserData(data);
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
    return <div className="flex min-h-screen items-center justify-center">Loading...</div>;
  }

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-gray-50 p-4">
      <Card className="w-full max-w-2xl">
        <CardHeader>
          <CardTitle className="text-2xl text-green-600">🎉 Welcome, {userData?.name}!</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <p>
            Welcome to the protected Dashboard! Your email is <strong>{userData?.email}</strong>.
            If you are seeing this, the backend verified your secure cookie.
          </p>
          <div className="rounded-md bg-muted p-4">
            <h3 className="font-semibold">How this is protected:</h3>
            <ul className="ml-4 mt-2 list-disc space-y-1 text-sm text-muted-foreground">
              <li>When the OTP succeeded, the backend told the browser to store a cookie.</li>
              <li>Every time you fetch data for this dashboard, the cookie is sent automatically.</li>
              <li>If the backend sees the cookie is missing or expired, it returns 401, and you get kicked back to Login.</li>
            </ul>
          </div>
          <Button onClick={() => navigate("/")} variant="outline">
            Go to Landing Page
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
