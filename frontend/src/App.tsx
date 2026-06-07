import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import AuthPage from "./pages/AuthPage";
import ProtectedRoute from "./components/ProtectedRoute";
import DashboardLayout from "./components/DashboardLayout";

// Dashboard Tabs
import HomeTab from "./pages/dashboard/HomeTab";
import MyBooksTab from "./pages/dashboard/MyBooksTab";
import BountiesTab from "./pages/dashboard/BountiesTab";
import ProfileTab from "./pages/dashboard/ProfileTab";
import ScanTab from "./pages/dashboard/ScanTab";
import BookDetailsTab from "./pages/dashboard/BookDetailsTab";

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<AuthPage />} />
        <Route path="/signup" element={<AuthPage />} />
        
        {/* Protected Dashboard Routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/dashboard" element={<DashboardLayout />}>
            <Route index element={<HomeTab />} />
            <Route path="my-books" element={<MyBooksTab />} />
            <Route path="books/:id" element={<BookDetailsTab />} />
            <Route path="bounties" element={<BountiesTab />} />
            <Route path="profile" element={<ProfileTab />} />
            <Route path="scan" element={<ScanTab />} />
          </Route>
        </Route>

        {/* Catch-all redirect to home */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </Router>
  );
}

export default App;
