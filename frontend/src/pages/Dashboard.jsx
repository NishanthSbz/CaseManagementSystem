import { useEffect } from 'react';
import { Outlet, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';
import { Navbar } from '../components/Navbar';

export const Dashboard = () => {
  const { isAuthenticated, checkAuth } = useAuthStore();
  const navigate = useNavigate();

  useEffect(() => {
    const verifyAuth = async () => {
      if (!isAuthenticated) {
        const isValid = await checkAuth();
        if (!isValid) {
          navigate('/login');
        }
      }
    };

    verifyAuth();
  }, [isAuthenticated, checkAuth, navigate]);

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <Outlet />
        </div>
      </main>
    </div>
  );
};