import { useState, useEffect } from 'react';
import type { ReactNode } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  ShoppingBag,
  UtensilsCrossed,
  Users,
  LogOut,
  Menu,
  X,
  Tag,
  BarChart3,
  MessageSquare,
  Sun,
  Moon,
} from 'lucide-react';
import { useTheme } from '../hooks/useTheme';

interface LayoutProps {
  children: ReactNode;
}

const navigationItems = [
  { name: 'Огляд', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Товари', href: '/menu', icon: UtensilsCrossed },
  { name: 'Промокоди', href: '/promo', icon: Tag },
  { name: 'Аналітика', href: '/analytics', icon: BarChart3 },
  { name: 'Відгуки', href: '/reviews', icon: MessageSquare },
];

export default function Layout({ children }: LayoutProps) {
  const location = useLocation();
  const navigate = useNavigate();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const { theme, toggleTheme } = useTheme();

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      const target = event.target as HTMLElement;
      if (!target.closest('.user-menu-container')) {
        setUserMenuOpen(false);
      }
    };

    if (userMenuOpen) {
      document.addEventListener('click', handleClickOutside);
      return () => document.removeEventListener('click', handleClickOutside);
    }
  }, [userMenuOpen]);

  const handleLogout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user_role');
    navigate('/login');
    setUserMenuOpen(false);
  };

  return (
    <div className="min-h-screen bg-neutral-100 dark:bg-neutral-950">
      {/* Header - Same style as client site */}
      <header className="bg-white/95 dark:bg-neutral-900/95 backdrop-blur-sm sticky top-0 z-50 border-b border-neutral-200/50 dark:border-neutral-700/50 transition-all duration-300">
        <div className="max-w-[1920px] mx-auto px-6 md:px-12 lg:px-16 xl:px-20">
          <div className="flex items-center justify-between h-14 md:h-16">
            {/* Left - Mobile Menu Button */}
                  <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden p-2 text-neutral-900 dark:text-neutral-100 hover:text-black dark:hover:text-white transition-colors duration-200"
              aria-label="Меню"
            >
              <Menu className="w-5 h-5 md:w-6 md:h-6" />
                  </button>

            {/* Center - Logo */}
            <Link
              to="/dashboard"
              className="absolute left-1/2 -translate-x-1/2 text-lg md:text-xl font-black text-black dark:text-white tracking-[0.08em] hover:opacity-70 transition-opacity duration-200 uppercase"
            >
              Men's Clothes Admin
            </Link>

            {/* Right - Navigation */}
            <nav className="flex items-center gap-3 md:gap-4 ml-auto">
              {/* Desktop Navigation */}
              <div className="hidden lg:flex items-center gap-2">
                {navigationItems.map((item) => {
                        const Icon = item.icon;
                        const isActive = location.pathname === item.href;
                        return (
                          <Link
                            key={item.name}
                            to={item.href}
                      className={`px-3 py-2 text-sm font-medium transition-colors duration-200 ${
                              isActive
                          ? 'text-black dark:text-white border-b-2 border-black dark:border-white'
                          : 'text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white'
                            }`}
                          >
                      {item.name}
                          </Link>
                        );
                      })}
              </div>

              {/* Theme Toggle */}
              <button
                onClick={toggleTheme}
                className="p-2 text-neutral-600 hover:text-black dark:text-neutral-400 dark:hover:text-white transition-colors"
                aria-label="Переключити тему"
              >
                {theme === 'light' ? (
                  <Moon className="w-5 h-5 md:w-6 md:h-6" />
                ) : (
                  <Sun className="w-5 h-5 md:w-6 md:h-6" />
                )}
              </button>

              {/* User Menu */}
              <div className="relative user-menu-container">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="p-2 text-neutral-600 dark:text-neutral-400 hover:text-black dark:hover:text-white transition-colors duration-200"
                  aria-label="Меню користувача"
                >
                  <Users className="w-5 h-5 md:w-6 md:h-6" />
                </button>
                {userMenuOpen && (
                  <div className="absolute right-0 top-full mt-2 w-48 bg-white dark:bg-neutral-800 border border-neutral-200 dark:border-neutral-700 shadow-xl rounded-sm overflow-hidden z-50 animate-scale-in">
                    <button
                      onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 dark:text-neutral-300 hover:bg-neutral-50 dark:hover:bg-neutral-700 hover:text-black dark:hover:text-white transition-colors duration-200"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Вихід</span>
                    </button>
                    </div>
                  )}
                </div>
            </nav>
          </div>
        </div>
      </header>

      {/* Mobile Menu */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <div className="fixed inset-0 bg-black/70 backdrop-blur-md" onClick={() => setMobileMenuOpen(false)} />
          <div className="fixed inset-y-0 left-0 w-full max-w-xs bg-white dark:bg-neutral-900 shadow-2xl">
            <div className="flex h-14 items-center justify-between px-6 border-b border-neutral-200 dark:border-neutral-700">
              <h1 className="text-base font-black text-black dark:text-white tracking-tight uppercase">Men's Clothes Admin</h1>
                <button
                onClick={() => setMobileMenuOpen(false)}
                className="text-neutral-400 dark:text-neutral-500 hover:text-black dark:hover:text-white transition-colors"
              >
                <X className="w-6 h-6" />
                </button>
            </div>
            <nav className="p-4 space-y-1">
              {navigationItems.map((item) => {
                      const Icon = item.icon;
                      const isActive = location.pathname === item.href;
                      return (
                        <Link
                          key={item.name}
                          to={item.href}
                    onClick={() => setMobileMenuOpen(false)}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                            isActive
                        ? 'bg-neutral-900 dark:bg-white text-white dark:text-neutral-900 font-semibold shadow-md'
                        : 'text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-black dark:hover:text-white'
                          }`}
                        >
                          <Icon className="w-5 h-5" />
                          <span className="font-medium">{item.name}</span>
                        </Link>
                      );
                    })}
          </nav>
            <div className="p-4 border-t border-neutral-200 dark:border-neutral-700">
            <button
              onClick={handleLogout}
                className="flex items-center gap-3 px-4 py-3 w-full rounded-lg text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-800 hover:text-black dark:hover:text-white transition-colors"
            >
              <LogOut className="w-5 h-5" />
                <span className="font-medium">Вийти</span>
            </button>
          </div>
        </div>
      </div>
      )}

      {/* Main content */}
      <main className="p-6 lg:p-10 bg-neutral-100 dark:bg-neutral-950 min-h-screen flex flex-col">
        <div className="flex-1 flex flex-col">
          <div className="flex-1 flex items-start justify-center">
            <div className="w-full max-w-[1600px]">
              {children}
            </div>
          </div>
        </div>
        </main>
    </div>
  );
}
