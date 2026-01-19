import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import { LogIn, AlertCircle } from 'lucide-react';

export default function Login() {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/auth/login', { username, password });
      
      // Перевірка ролі - тільки адміністратори можуть входити
      const userRole = response.data.user?.role;
      if (userRole === 'client') {
        setError('Access denied. Only administrators can access this panel.');
        setLoading(false);
        return;
      }
      
      if (userRole !== 'system_admin' && userRole !== 'manager') {
        setError('Access denied. Insufficient permissions.');
        setLoading(false);
        return;
      }
      
      localStorage.setItem('token', response.data.access_token);
      localStorage.setItem('user_role', userRole);
      navigate('/dashboard');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-neutral-50 via-white to-neutral-100 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white rounded-3xl shadow-2xl border border-neutral-200 overflow-hidden">
          {/* Header with gradient */}
          <div className="bg-gradient-to-r from-neutral-900 via-neutral-800 to-neutral-900 px-8 py-10 text-center">
            <div className="inline-flex items-center justify-center w-20 h-20 bg-white/10 backdrop-blur-sm rounded-2xl mb-4 border border-white/20">
              <LogIn className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-4xl font-black text-white mb-2 tracking-tight">MEN'S CLOTHES</h1>
            <p className="text-neutral-300 text-sm font-medium uppercase tracking-wider">Admin Portal</p>
          </div>

          <div className="p-8">
            {error && (
              <div className="mb-6 p-4 bg-neutral-50 border-l-4 border-neutral-900 rounded-lg flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-neutral-900 mt-0.5 flex-shrink-0" />
                <p className="text-sm text-neutral-800 font-medium">{error}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-5">
              <div>
                <label htmlFor="username" className="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-2">
                  Username
                </label>
                <input
                  id="username"
                  type="text"
                  required
                  value={username}
                  onChange={(e) => setUsername(e.target.value)}
                  className="w-full px-4 py-3.5 bg-neutral-50 border-2 border-neutral-200 rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 transition-all font-medium text-neutral-900 placeholder:text-neutral-400"
                  placeholder="Enter your username"
                />
              </div>

              <div>
                <label htmlFor="password" className="block text-xs font-bold text-neutral-700 uppercase tracking-wider mb-2">
                  Password
                </label>
                <input
                  id="password"
                  type="password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3.5 bg-neutral-50 border-2 border-neutral-200 rounded-xl focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 transition-all font-medium text-neutral-900 placeholder:text-neutral-400"
                  placeholder="Enter your password"
                />
              </div>

              <button
                type="submit"
                disabled={loading}
                className="w-full bg-gradient-to-r from-neutral-900 to-neutral-800 text-white py-4 px-6 rounded-xl font-bold text-sm uppercase tracking-wider hover:from-neutral-800 hover:to-neutral-700 focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg hover:shadow-xl"
              >
                {loading ? 'Signing in...' : 'Sign in'}
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  );
}

