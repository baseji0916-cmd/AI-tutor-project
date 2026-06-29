import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { GuestRoute, ProtectedRoute } from "@/components/layout/ProtectedRoute";
import { AuthProvider } from "@/stores/AuthContext";
import { AIPlanPage } from "@/pages/AIPlanPage";
import { DashboardPage } from "@/pages/DashboardPage";
import { GoalsPage } from "@/pages/GoalsPage";
import { GrowthDNAPage } from "@/pages/GrowthDNAPage";
import { LoginPage } from "@/pages/LoginPage";
import { MissionsPage } from "@/pages/MissionsPage";
import { MorePage } from "@/pages/MorePage";
import { ProgressPage } from "@/pages/ProgressPage";
import { RegisterPage } from "@/pages/RegisterPage";
import { SettingsPage } from "@/pages/SettingsPage";
import { SimulationPage } from "@/pages/SimulationPage";
import { TimelinePage } from "@/pages/TimelinePage";
import { TutorPage } from "@/pages/TutorPage";

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route element={<GuestRoute />}>
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
          </Route>

          <Route element={<ProtectedRoute />}>
            <Route element={<AppLayout />}>
              <Route path="/dashboard" element={<DashboardPage />} />
              <Route path="/goals" element={<GoalsPage />} />
              <Route path="/missions" element={<MissionsPage />} />
              <Route path="/ai-plan" element={<AIPlanPage />} />
              <Route path="/progress" element={<ProgressPage />} />
              <Route path="/growth-dna" element={<GrowthDNAPage />} />
              <Route path="/simulation" element={<SimulationPage />} />
              <Route path="/timeline" element={<TimelinePage />} />
              <Route path="/tutor" element={<TutorPage />} />
              <Route path="/settings" element={<SettingsPage />} />
              <Route path="/more" element={<MorePage />} />
              <Route path="/coach" element={<Navigate to="/tutor" replace />} />
            </Route>
          </Route>

          <Route path="/" element={<Navigate to="/dashboard" replace />} />
          <Route path="*" element={<Navigate to="/dashboard" replace />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
