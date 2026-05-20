import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { User, Mail, Phone, Shield, Calendar, Lock, Save, Check, AlertCircle } from 'lucide-react';
import api from '../api/client';
import { showSuccess, showError } from '../utils/notifications';

interface UserProfile {
  id: number;
  username: string;
  email: string | null;
  phone: string | null;
  name: string | null;
  role: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export default function Profile() {
  const navigate = useNavigate();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);

  // Edit form
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [phone, setPhone] = useState('');
  const [saving, setSaving] = useState(false);

  // Password change
  const [oldPassword, setOldPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [savingPassword, setSavingPassword] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem('client_token')) {
      navigate('/');
      return;
    }
    fetchProfile();
  }, [navigate]);

  const fetchProfile = async () => {
    try {
      const res = await api.get('/users/me');
      const data: UserProfile = res.data;
      setProfile(data);
      setName(data.name || '');
      setEmail(data.email || '');
      setPhone(data.phone || '');
    } catch (error) {
      console.error('Failed to fetch profile:', error);
      showError('Не вдалося завантажити профіль');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      const payload: Record<string, string> = {};
      if (name.trim()) payload.name = name.trim();
      if (email.trim()) payload.email = email.trim();
      if (phone.trim()) payload.phone = phone.trim();

      await api.put('/users/me', payload);
      showSuccess('Профіль оновлено');
      fetchProfile();
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Не вдалося оновити профіль');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();

    if (newPassword.length < 6) {
      showError('Новий пароль має бути не менше 6 символів');
      return;
    }

    if (newPassword !== confirmPassword) {
      showError('Паролі не співпадають');
      return;
    }

    setSavingPassword(true);
    try {
      await api.put('/users/me', {
        old_password: oldPassword,
        password: newPassword,
      });
      showSuccess('Пароль змінено');
      setOldPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Не вдалося змінити пароль');
    } finally {
      setSavingPassword(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-3xl mx-auto p-8">
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900 dark:border-neutral-100"></div>
        </div>
      </div>
    );
  }

  if (!profile) {
    return (
      <div className="max-w-3xl mx-auto p-8">
        <div className="text-center py-16">
          <AlertCircle className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">Помилка завантаження</h2>
          <p className="text-neutral-600 dark:text-neutral-400">Не вдалося завантажити дані профілю.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-3xl mx-auto p-4 md:p-8">
      <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white tracking-tight mb-8 uppercase">
        Профіль
      </h1>

      {/* User Info Card */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6 mb-6">
        <h2 className="text-sm font-black text-black dark:text-white uppercase tracking-[0.15em] mb-6">
          Інформація
        </h2>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center flex-shrink-0">
              <User className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
            </div>
            <div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wide">Логін</p>
              <p className="text-sm font-semibold text-neutral-900 dark:text-white">{profile.username}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center flex-shrink-0">
              <Shield className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
            </div>
            <div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wide">Роль</p>
              <p className="text-sm font-semibold text-neutral-900 dark:text-white capitalize">{profile.role}</p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center flex-shrink-0">
              <Calendar className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
            </div>
            <div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wide">Учасник з</p>
              <p className="text-sm font-semibold text-neutral-900 dark:text-white">
                {new Date(profile.created_at).toLocaleDateString('uk-UA', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric',
                })}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center flex-shrink-0">
              <Mail className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
            </div>
            <div>
              <p className="text-xs text-neutral-500 dark:text-neutral-400 uppercase tracking-wide">Email верифікація</p>
              {profile.is_verified ? (
                <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-green-700 dark:text-green-400">
                  <Check className="w-4 h-4" />
                  Підтверджено
                </span>
              ) : (
                <span className="inline-flex items-center gap-1.5 text-sm font-semibold text-amber-600 dark:text-amber-400">
                  <AlertCircle className="w-4 h-4" />
                  Не підтверджено
                </span>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Edit Profile Form */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6 mb-6">
        <h2 className="text-sm font-black text-black dark:text-white uppercase tracking-[0.15em] mb-6">
          Редагувати профіль
        </h2>
        <form onSubmit={handleSaveProfile} className="space-y-5">
          <div>
            <label className="flex items-center gap-2 text-xs font-bold text-black dark:text-white mb-2 uppercase tracking-[0.15em]">
              <User className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
              Ім'я
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="Ваше ім'я"
              className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent transition-all bg-white dark:bg-neutral-800 dark:text-white font-medium"
            />
          </div>

          <div>
            <label className="flex items-center gap-2 text-xs font-bold text-black dark:text-white mb-2 uppercase tracking-[0.15em]">
              <Mail className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="your@email.com"
              className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent transition-all bg-white dark:bg-neutral-800 dark:text-white font-medium"
            />
          </div>

          <div>
            <label className="flex items-center gap-2 text-xs font-bold text-black dark:text-white mb-2 uppercase tracking-[0.15em]">
              <Phone className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
              Телефон
            </label>
            <input
              type="tel"
              value={phone}
              onChange={(e) => setPhone(e.target.value)}
              placeholder="+380 XX XXX XX XX"
              className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent transition-all bg-white dark:bg-neutral-800 dark:text-white font-medium"
            />
          </div>

          <button
            type="submit"
            disabled={saving}
            className="w-full bg-black dark:bg-white text-white dark:text-black py-3.5 px-4 text-sm font-bold uppercase tracking-[0.15em] hover:bg-neutral-800 dark:hover:bg-neutral-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 rounded-lg flex items-center justify-center gap-2"
          >
            {saving ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 dark:border-black/30 border-t-white dark:border-t-black rounded-full animate-spin" />
                Збереження...
              </>
            ) : (
              <>
                <Save className="w-4 h-4" />
                Зберегти зміни
              </>
            )}
          </button>
        </form>
      </div>

      {/* Change Password */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-6">
        <h2 className="text-sm font-black text-black dark:text-white uppercase tracking-[0.15em] mb-6">
          Змінити пароль
        </h2>
        <form onSubmit={handleChangePassword} className="space-y-5">
          <div>
            <label className="flex items-center gap-2 text-xs font-bold text-black dark:text-white mb-2 uppercase tracking-[0.15em]">
              <Lock className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
              Поточний пароль
            </label>
            <input
              type="password"
              value={oldPassword}
              onChange={(e) => setOldPassword(e.target.value)}
              required
              placeholder="Введіть поточний пароль"
              autoComplete="current-password"
              className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent transition-all bg-white dark:bg-neutral-800 dark:text-white font-medium"
            />
          </div>

          <div>
            <label className="flex items-center gap-2 text-xs font-bold text-black dark:text-white mb-2 uppercase tracking-[0.15em]">
              <Lock className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
              Новий пароль
            </label>
            <input
              type="password"
              value={newPassword}
              onChange={(e) => setNewPassword(e.target.value)}
              required
              minLength={6}
              placeholder="Мінімум 6 символів"
              autoComplete="new-password"
              className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent transition-all bg-white dark:bg-neutral-800 dark:text-white font-medium"
            />
          </div>

          <div>
            <label className="flex items-center gap-2 text-xs font-bold text-black dark:text-white mb-2 uppercase tracking-[0.15em]">
              <Lock className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
              Підтвердити пароль
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              required
              placeholder="Повторіть новий пароль"
              autoComplete="new-password"
              className="w-full px-4 py-3 text-sm border border-neutral-200 dark:border-neutral-700 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent transition-all bg-white dark:bg-neutral-800 dark:text-white font-medium"
            />
            {confirmPassword && newPassword !== confirmPassword && (
              <p className="mt-2 text-xs text-red-600 dark:text-red-400 font-medium">Паролі не співпадають</p>
            )}
          </div>

          <button
            type="submit"
            disabled={savingPassword}
            className="w-full bg-black dark:bg-white text-white dark:text-black py-3.5 px-4 text-sm font-bold uppercase tracking-[0.15em] hover:bg-neutral-800 dark:hover:bg-neutral-200 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 rounded-lg flex items-center justify-center gap-2"
          >
            {savingPassword ? (
              <>
                <div className="w-4 h-4 border-2 border-white/30 dark:border-black/30 border-t-white dark:border-t-black rounded-full animate-spin" />
                Збереження...
              </>
            ) : (
              <>
                <Lock className="w-4 h-4" />
                Змінити пароль
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  );
}
