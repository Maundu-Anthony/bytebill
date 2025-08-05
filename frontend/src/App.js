import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import Layout from './components/Layout';
import Login from './pages/Login';
import Dashboard from './pages/Dashboard';
import VoucherManagement from './pages/VoucherManagement';
import UserManagement from './pages/UserManagement';
import ISPMonitoring from './pages/ISPMonitoring';
import SessionManagement from './pages/SessionManagement';
import Settings from './pages/Settings';
import CaptivePortal from './pages/CaptivePortal';

function App() {
  return (
    <AuthProvider>
      <Router>
        <div className="min-h-screen bg-gray-50">
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/portal" element={<CaptivePortal />} />
            <Route path="/" element={<Layout />}>
              <Route index element={<Dashboard />} />
              <Route path="dashboard" element={<Dashboard />} />
              <Route path="vouchers" element={<VoucherManagement />} />
              <Route path="users" element={<UserManagement />} />
              <Route path="sessions" element={<SessionManagement />} />
              <Route path="isp" element={<ISPMonitoring />} />
              <Route path="settings" element={<Settings />} />
            </Route>
          </Routes>
        </div>
      </Router>
    </AuthProvider>
  );
}

export default App;
