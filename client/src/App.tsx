import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import type { MenuItem, Category } from './types';
import api from './api/client';
import { ShoppingCart, User, Package, Home, LogOut, Search, X, ChevronRight, LayoutGrid, Eye, EyeOff } from 'lucide-react';
import { useDebounce } from './hooks/useDebounce';
import { showSuccess, showError } from './utils/notifications';
import Cart from './pages/Cart';
import Orders from './pages/Orders';

function Header() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('client_token');
  const user = localStorage.getItem('client_user');
  const username = user ? JSON.parse(user).username : '';
  const [cartCount, setCartCount] = useState(0);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [authMode, setAuthMode] = useState<'login' | 'register'>('login');

  useEffect(() => {
    if (isLoggedIn) {
      fetchCartCount();
      
      // Оновлюємо кошик кожні 2 секунди для динамічного оновлення
      const interval = setInterval(fetchCartCount, 2000);
      return () => clearInterval(interval);
    }
  }, [isLoggedIn]);

  // Close user menu when clicking outside
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
  }, [userMenuOpen, isLoggedIn]);

  const fetchCartCount = async () => {
    try {
      const response = await api.get('/cart/me');
      setCartCount(response.data.items.length);
    } catch (error) {
      // Тихо ігноруємо помилку
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('client_token');
    localStorage.removeItem('client_user');
    navigate('/');
    setUserMenuOpen(false);
  };

  return (
    <header className="bg-white/95 backdrop-blur-sm sticky top-0 z-50 border-b border-neutral-200/50 transition-all duration-300">
      <div className="max-w-[1920px] mx-auto px-6 md:px-12 lg:px-16 xl:px-20">
        <div className="flex items-center justify-between h-14 md:h-16">
          {/* Center - Logo */}
          <Link to="/" className="absolute left-1/2 -translate-x-1/2 text-lg md:text-xl font-black text-black tracking-[0.08em] hover:opacity-70 transition-opacity duration-200 uppercase">
            Men's Clothes
          </Link>

          {/* Right Icons - All grouped together */}
          <nav className="flex items-center gap-3 md:gap-4 ml-auto">
            <Link to="/" className="p-2 text-neutral-900 hover:text-black transition-colors duration-200" title="Каталог">
              <LayoutGrid className="w-5 h-5 md:w-6 md:h-6" />
            </Link>
              <div className="relative user-menu-container">
                <button
                  onClick={() => setUserMenuOpen(!userMenuOpen)}
                  className="relative p-2 text-neutral-600 hover:text-black transition-colors duration-200"
                  aria-label="User menu"
                >
                  <User className="w-5 h-5 md:w-6 md:h-6" />
                {isLoggedIn && cartCount > 0 && (
                    <span className="absolute -top-1 -right-1 w-5 h-5 bg-black text-white text-[10px] font-bold rounded-full flex items-center justify-center animate-scale-in">
                      {cartCount}
                    </span>
                  )}
                </button>
                {userMenuOpen && (
                isLoggedIn ? (
                  <div className="absolute right-0 top-full mt-2 w-48 bg-white border border-neutral-200 shadow-xl rounded-sm overflow-hidden z-50 animate-scale-in">
                    <Link
                      to="/cart"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center justify-between px-4 py-3 text-sm font-medium text-neutral-700 hover:bg-neutral-50 hover:text-black transition-colors duration-200"
                    >
                      <div className="flex items-center gap-3">
                        <ShoppingCart className="w-4 h-4" />
                        <span>Кошик</span>
                      </div>
              {cartCount > 0 && (
                        <span className="w-5 h-5 bg-black text-white text-[10px] font-bold rounded-full flex items-center justify-center">
                  {cartCount}
                </span>
              )}
            </Link>
                    <Link
                      to="/orders"
                      onClick={() => setUserMenuOpen(false)}
                      className="flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 hover:bg-neutral-50 hover:text-black transition-colors duration-200 border-t border-neutral-100"
                    >
                      <Package className="w-4 h-4" />
                      <span>Мої замовлення</span>
                </Link>
                  <button
                    onClick={handleLogout}
                      className="w-full flex items-center gap-3 px-4 py-3 text-sm font-medium text-neutral-700 hover:bg-neutral-50 hover:text-black transition-colors duration-200 border-t border-neutral-100"
                  >
                      <LogOut className="w-4 h-4" />
                      <span>Вихід</span>
                  </button>
              </div>
            ) : (
                  <AuthDropdown
                  mode={authMode}
                  onSwitchMode={(mode) => setAuthMode(mode)}
                  onSuccess={() => {
                      setUserMenuOpen(false);
                    navigate('/');
                    window.location.reload();
                  }}
                />
                )
            )}
            </div>
          </nav>
        </div>
      </div>
    </header>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-white overflow-x-hidden w-full">
        <Header />

        {/* Main Content */}
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Cart />} />
            <Route path="/orders" element={<Orders />} />
          </Routes>
        </main>

        {/* Липкий кошик для мобільних (тільки на головній сторінці) */}
        <FloatingCart />

        {/* Footer - Minimal Nike Style */}
        <footer className="bg-white border-t border-neutral-200 mt-20 md:mt-24">
          <div className="max-w-[1920px] mx-auto px-6 md:px-12 lg:px-16 xl:px-20 py-6 md:py-8">
            <p className="text-xs text-neutral-500 text-center uppercase tracking-wide">
              © 2025 Sport Store. Всі права захищені.
            </p>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

// Home Page with Menu - Premium Redesign
function HomePage() {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState<'name' | 'price_asc' | 'price_desc'>('name');
  const debouncedSearchQuery = useDebounce(searchQuery, 300);

  useEffect(() => {
    fetchCategories();
    fetchMenu();
  }, []);

  const fetchCategories = async () => {
    try {
      const response = await api.get('/categories/');
      setCategories(response.data);
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  };

  const fetchMenu = async (categoryId: number | null = null) => {
    try {
      const params = categoryId ? { category_id: categoryId } : {};
      const response = await api.get('/products/', { params });
      setMenuItems(response.data);
    } catch (error) {
      console.error('Failed to fetch menu:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryClick = (categoryId: number | null) => {
    setSelectedCategory(categoryId);
    setLoading(true);
    fetchMenu(categoryId);
  };

  // Фільтрація та сортування
  const getFilteredAndSortedItems = () => {
    let items = [...menuItems];

    // Пошук
    if (debouncedSearchQuery) {
      const query = debouncedSearchQuery.toLowerCase();
      items = items.filter(
        (item) =>
          item.name.toLowerCase().includes(query) ||
          item.description?.toLowerCase().includes(query)
      );
    }

    // Сортування
    items.sort((a, b) => {
      if (sortBy === 'price_asc') return a.price - b.price;
      if (sortBy === 'price_desc') return b.price - a.price;
      return a.name.localeCompare(b.name, 'uk');
    });

    return items;
  };

  const addToCart = async (item: MenuItem) => {
    // Check if user is logged in
    if (!localStorage.getItem('client_token')) {
      showError('Для додавання в кошик потрібно увійти. Натисніть на іконку користувача для входу.');
      return;
    }

    try {
      await api.post('/cart/me/items', {
        menu_item_id: item.id,
        quantity: 1,
        price: item.price,
      });

      showSuccess(`${item.name} додано в кошик`);
    } catch (error) {
      console.error('Failed to add to cart:', error);
      showError('Не вдалося додати в кошик');
    }
  };

  const filteredItems = getFilteredAndSortedItems();
  // Featured section shows only first item if items exist and not loading

  return (
    <div className="bg-white min-h-screen">
      {/* Main Catalog Section with Sidebar */}
      <div className="max-w-[1920px] mx-auto px-4 md:px-8 lg:px-12 xl:px-16 pb-20 md:pb-32">
        <div className="grid grid-cols-1 lg:grid-cols-[220px_1fr] gap-8 md:gap-10 lg:gap-12 xl:gap-16">
          
          {/* Sidebar - Filters & Categories - Compact Design */}
          <aside className="hidden lg:block">
            <div className="sticky top-20 z-40 space-y-10 animate-slide-in-left">
              {/* Search - Compact */}
              <div className="group">
          <div className="relative">
                  <Search className="absolute left-0 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 group-focus-within:text-black transition-all duration-300 group-focus-within:scale-110" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
                    placeholder="Шукати товари..."
                    className="w-full pl-7 pr-10 py-3 text-sm bg-transparent border-b border-neutral-200 focus:border-black focus:outline-none transition-all duration-300 placeholder:text-neutral-400 focus:placeholder:text-neutral-300 font-medium"
            />
            {searchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                      className="absolute right-0 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-black transition-all duration-300 hover:scale-125 active:scale-95"
                      aria-label="Очистити пошук"
              >
                      <X className="w-5 h-5" />
              </button>
            )}
          </div>
              </div>

              {/* Categories - Compact Design */}
              {categories.length > 0 && (
                <div>
                  <div className="space-y-1">
                    <button
                      onClick={() => handleCategoryClick(null)}
                      className={`group w-full text-left px-4 py-3 text-sm font-medium transition-all duration-300 uppercase tracking-wide relative overflow-hidden ${
                        selectedCategory === null
                          ? 'text-black bg-neutral-100'
                          : 'text-neutral-500 hover:text-black hover:bg-neutral-50'
                      }`}
                    >
                      <span className="relative z-10 flex items-center justify-between">
                        <span>Всі товари</span>
                        {selectedCategory === null && (
                          <ChevronRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                        )}
                      </span>
                      {selectedCategory === null && (
                        <span className="absolute inset-0 bg-gradient-to-r from-transparent via-black/5 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></span>
                      )}
                    </button>
                    {categories.map((category, idx) => (
                      <button
                        key={category.id}
                        onClick={() => handleCategoryClick(category.id)}
                        className={`group w-full text-left px-4 py-3 text-sm font-medium transition-all duration-300 uppercase tracking-wide relative overflow-hidden ${
                          selectedCategory === category.id
                            ? 'text-black bg-neutral-100'
                            : 'text-neutral-500 hover:text-black hover:bg-neutral-50'
                        }`}
                        style={{ animationDelay: `${idx * 0.05}s` }}
                      >
                        <span className="relative z-10 flex items-center justify-between">
                          <span>{category.name}</span>
                          {selectedCategory === category.id && (
                            <ChevronRight className="w-5 h-5 opacity-0 group-hover:opacity-100 transition-opacity duration-300" />
                          )}
                        </span>
                        {selectedCategory === category.id && (
                          <span className="absolute inset-0 bg-gradient-to-r from-transparent via-black/5 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-700"></span>
                        )}
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Sort - Compact */}
              <div>
                <div className="relative">
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as any)}
                    className="w-full px-4 py-3 text-sm border border-neutral-200 focus:ring-1 focus:ring-black focus:border-black font-medium text-neutral-900 cursor-pointer bg-white hover:border-neutral-400 transition-all duration-300 appearance-none focus:outline-none"
              >
                <option value="name">За назвою</option>
                    <option value="price_asc">Ціна: від дешевих</option>
                    <option value="price_desc">Ціна: від дорогих</option>
              </select>
                  <ChevronRight className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 pointer-events-none rotate-90" />
            </div>
              </div>
          </div>
          </aside>

          {/* Main Content */}
          <div className="min-w-0">
            {/* Products Grid - Premium Layout */}
        {loading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-4 gap-5 md:gap-6 lg:gap-8">
                {[1, 2, 3, 4, 5, 6, 7, 8, 9, 10].map((i) => (
                  <div key={i} className="flex flex-col animate-pulse">
                    <div className="w-full aspect-square bg-gradient-to-br from-neutral-100 to-neutral-200 mb-4 rounded-sm"></div>
                    <div className="space-y-3">
                      <div className="h-4 bg-neutral-100 rounded w-3/4"></div>
                      <div className="h-5 bg-neutral-100 rounded w-1/3"></div>
                </div>
              </div>
            ))}
          </div>
        ) : getFilteredAndSortedItems().length === 0 ? (
              <div className="text-center py-24 animate-fade-in">
                <div className="text-7xl mb-6 animate-scale-in">😔</div>
                <p className="text-black text-xl md:text-2xl mb-3 font-semibold">
                  {debouncedSearchQuery ? 'Нічого не знайдено' : 'Каталог тимчасово недоступний'}
                </p>
                <p className="text-neutral-600 text-base md:text-lg mb-8">
              {debouncedSearchQuery
                ? 'Спробуйте змінити запит або очистити фільтри'
                : 'Будь ласка, зайдіть пізніше'}
            </p>
            {debouncedSearchQuery && (
              <button
                onClick={() => setSearchQuery('')}
                    className="inline-flex items-center gap-2 bg-black text-white px-6 py-3 rounded-md font-medium hover:bg-neutral-800 transition-all duration-200 hover:scale-105 active:scale-95"
              >
                <X className="w-5 h-5" />
                Очистити пошук
              </button>
            )}
          </div>
            ) : !loading && filteredItems.length > 0 ? (
              <div 
                className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-4 xl:grid-cols-4 gap-5 md:gap-6 lg:gap-8"
              >
                {filteredItems.map((item, index) => (
                  <div 
                    key={item.id} 
                    className="group flex flex-col cursor-pointer"
                  >
                    {/* Image Container - Premium Card */}
                    <div className="relative overflow-hidden bg-white mb-4 aspect-square rounded-sm shadow-sm group-hover:shadow-xl transition-all duration-500">
                  {item.image_url ? (
                        <>
                    <img 
                      src={item.image_url} 
                      alt={item.name} 
                            className="w-full h-full object-cover transition-transform duration-[800ms] ease-[cubic-bezier(0.16,1,0.3,1)] group-hover:scale-115"
                            loading="lazy"
                          />
                          {/* Premium Overlay */}
                          <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                          {/* Quick Add Button */}
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              addToCart(item);
                            }}
                            className="absolute bottom-4 left-1/2 -translate-x-1/2 opacity-0 group-hover:opacity-100 transform translate-y-4 group-hover:translate-y-0 transition-all duration-300 bg-white text-black px-6 py-2.5 font-black text-xs uppercase tracking-wide hover:scale-110 active:scale-95 shadow-xl"
                          >
                            <span className="flex items-center gap-2">
                              <ShoppingCart className="w-4 h-4" />
                              Додати
                            </span>
                          </button>
                        </>
                      ) : (
                        <div className="w-full h-full bg-gradient-to-br from-neutral-50 to-neutral-100 flex items-center justify-center">
                          <span className="text-6xl text-neutral-200 animate-float" style={{ animationDelay: `${index * 0.1}s` }}>👟</span>
                        </div>
                      )}
                    </div>

                    {/* Content - Enhanced Typography */}
                    <div className="flex flex-col flex-1 px-1">
                      <h3 className="text-sm md:text-base font-semibold text-black mb-1 tracking-tight leading-snug group-hover:opacity-80 transition-opacity duration-300 line-clamp-2">
                        {item.name}
                      </h3>

                      {item.description && (
                        <p className="text-[11px] md:text-xs text-neutral-600 mb-1 line-clamp-2 leading-snug">
                          {item.description}
                        </p>
                      )}

                      <div className="mt-auto">
                        <span className="text-base md:text-lg font-black text-black tracking-tight">
                      ₴{(item.price / 100).toFixed(0)}
                    </span>
                  </div>
                </div>
                  </div>
                ))}
                </div>
            ) : (
              <div className="text-center py-20">
                <p className="text-neutral-600">Немає інших товарів для відображення</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Auth Dropdown Component - Form in dropdown menu
function AuthDropdown({ 
  mode, 
  onSwitchMode,
  onSuccess 
}: { 
  mode: 'login' | 'register';
  onSwitchMode: (mode: 'login' | 'register') => void;
  onSuccess: () => void;
}) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  useEffect(() => {
    // Reset form when mode changes
    setUsername('');
    setPassword('');
    setConfirmPassword('');
    setError('');
    setShowPassword(false);
    setShowConfirmPassword(false);
  }, [mode]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (loading) return; // Запобігаємо повторній відправці
    
    setError('');
    setLoading(true);

    try {
      const response = await api.post('/auth/login', { username, password });
      localStorage.setItem('client_token', response.data.access_token);
      localStorage.setItem('client_user', JSON.stringify(response.data.user));
      setLoading(false);
      // Тільки при успішному вході викликаємо onSuccess
      onSuccess();
    } catch (err: any) {
      setLoading(false);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || 'Невірний логін або пароль';
      setError(errorMessage);
      // НЕ викликаємо onSuccess при помилці - залишаємо dropdown відкритим
      // НЕ перезавантажуємо сторінку
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    e.stopPropagation();
    
    if (loading) return; // Запобігаємо повторній відправці
    
    setError('');

    if (password !== confirmPassword) {
      setError('Паролі не співпадають');
      return;
    }

    if (password.length < 6) {
      setError('Пароль має бути не менше 6 символів');
      return;
    }

    setLoading(true);

    try {
      await api.post('/auth/register', { username, password });
      const loginResponse = await api.post('/auth/login', { username, password });
      localStorage.setItem('client_token', loginResponse.data.access_token);
      localStorage.setItem('client_user', JSON.stringify(loginResponse.data.user));
      setLoading(false);
      showSuccess(`Вітаємо, ${username}! Реєстрація успішна`);
      // Тільки при успішній реєстрації викликаємо onSuccess
      onSuccess();
    } catch (err: any) {
      setLoading(false);
      const errorMessage = err.response?.data?.detail || err.response?.data?.message || 'Помилка реєстрації';
      setError(errorMessage);
      // НЕ викликаємо onSuccess при помилці - залишаємо dropdown відкритим
      // НЕ перезавантажуємо сторінку
    }
  };

  return (
    <div className="absolute right-0 top-full mt-2 w-96 bg-white border border-neutral-200 shadow-2xl rounded-sm overflow-hidden z-50 animate-scale-in">
        <div className="p-6">
        {/* Header */}
        <div className="mb-5">
            <h2 className="text-lg font-black text-black mb-1 uppercase tracking-[0.1em]">
              {mode === 'login' ? 'Вхід' : 'Реєстрація'}
            </h2>
          </div>

          {/* Error message */}
          {error && (
          <div className="mb-4 p-3 bg-red-50 border-l-4 border-red-500 flex items-start gap-2 rounded-sm">
            <X className="w-4 h-4 text-red-600 mt-0.5 flex-shrink-0" />
            <p className="text-sm text-red-800 leading-relaxed font-medium">{error}</p>
            </div>
          )}

          {/* Form */}
        <form onSubmit={mode === 'login' ? handleLogin : handleRegister} className="space-y-4" noValidate>
            {/* Username */}
            <div>
            <label htmlFor="dropdown-auth-username" className="block text-xs font-bold text-black mb-2 uppercase tracking-[0.15em]">
                Логін
              </label>
              <input
              id="dropdown-auth-username"
                type="text"
                required
                minLength={mode === 'register' ? 3 : undefined}
                value={username}
                onChange={(e) => setUsername(e.target.value)}
              className="w-full px-4 py-3 text-sm border-b-2 border-neutral-200 focus:border-black focus:outline-none transition-all duration-200 bg-transparent font-medium"
                placeholder={mode === 'register' ? 'Мінімум 3 символи' : 'Введіть логін'}
              autoComplete="username"
              />
            </div>

            {/* Password */}
            <div>
            <label htmlFor="dropdown-auth-password" className="block text-xs font-bold text-black mb-2 uppercase tracking-[0.15em]">
                Пароль
              </label>
              <div className="relative">
                <input
                id="dropdown-auth-password"
                  type={showPassword ? 'text' : 'password'}
                  required
                  minLength={mode === 'register' ? 6 : undefined}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 pr-10 text-sm border-b-2 border-neutral-200 focus:border-black focus:outline-none transition-all duration-200 bg-transparent font-medium"
                  placeholder={mode === 'register' ? 'Мінімум 6 символів' : 'Введіть пароль'}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-black transition-colors duration-200 p-1"
                aria-label={showPassword ? 'Приховати пароль' : 'Показати пароль'}
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Confirm Password (only for register) */}
            {mode === 'register' && (
              <div>
              <label htmlFor="dropdown-auth-confirm-password" className="block text-xs font-bold text-black mb-2 uppercase tracking-[0.15em]">
                  Підтвердіть пароль
                </label>
                <div className="relative">
                  <input
                  id="dropdown-auth-confirm-password"
                    type={showConfirmPassword ? 'text' : 'password'}
                    required
                    value={confirmPassword}
                    onChange={(e) => setConfirmPassword(e.target.value)}
                  className="w-full px-4 py-3 pr-10 text-sm border-b-2 border-neutral-200 focus:border-black focus:outline-none transition-all duration-200 bg-transparent font-medium"
                    placeholder="Повторіть пароль"
                  autoComplete="new-password"
                  />
                  <button
                    type="button"
                    onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-neutral-400 hover:text-black transition-colors duration-200 p-1"
                  aria-label={showConfirmPassword ? 'Приховати пароль' : 'Показати пароль'}
                  >
                    {showConfirmPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                  </button>
                </div>
                {confirmPassword && password !== confirmPassword && (
                <p className="mt-2 text-xs text-red-600 font-medium">Паролі не співпадають</p>
                )}
              </div>
            )}

            {/* Submit button */}
            <button
              type="submit"
              disabled={loading}
            className="w-full bg-black text-white py-3.5 px-4 text-sm font-bold uppercase tracking-[0.15em] hover:bg-neutral-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 mt-6"
            >
              {loading ? (mode === 'login' ? 'Вхід...' : 'Реєстрація...') : (mode === 'login' ? 'Увійти' : 'Зареєструватись')}
            </button>
          </form>

          {/* Switch mode */}
          <div className="mt-5 pt-5 border-t border-neutral-200 text-center">
            <button
              type="button"
              onClick={() => {
                onSwitchMode(mode === 'login' ? 'register' : 'login');
                setError('');
              }}
            className="text-xs text-neutral-500 hover:text-black transition-colors duration-200 uppercase tracking-[0.1em]"
            >
              {mode === 'login' ? (
                <>Ще не маєте акаунту? <span className="font-bold text-black">Зареєструватись</span></>
              ) : (
                <>Вже маєте акаунт? <span className="font-bold text-black">Увійти</span></>
              )}
            </button>
        </div>
      </div>
    </div>
  );
}

// Floating Cart Component для мобільних
function FloatingCart() {
  const [cartCount, setCartCount] = useState(0);
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  useEffect(() => {
    const loggedIn = !!localStorage.getItem('client_token');
    setIsLoggedIn(loggedIn);
    
    if (loggedIn) {
      fetchCartCount();
      
      // Оновлюємо кожні 10 секунд
      const interval = setInterval(fetchCartCount, 10000);
      return () => clearInterval(interval);
    }
  }, []);

  const fetchCartCount = async () => {
    try {
      const response = await api.get('/cart/me');
      setCartCount(response.data.items.length);
    } catch (error) {
      // Тихо ігноруємо
    }
  };

  if (!isLoggedIn || cartCount === 0) return null;

  return (
    <Link
      to="/cart"
      className="lg:hidden fixed bottom-6 right-6 z-40 bg-black hover:bg-neutral-800 text-white px-6 py-4 rounded-md shadow-2xl transition-all flex items-center gap-3 font-semibold animate-bounce-subtle"
    >
      <ShoppingCart className="w-5 h-5 md:w-6 md:h-6" />
      <span className="text-base md:text-lg">{cartCount}</span>
    </Link>
  );
}

export default App;
