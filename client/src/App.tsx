import { BrowserRouter, Routes, Route, Link, useNavigate } from 'react-router-dom';
import { useEffect, useState } from 'react';
import type { MenuItem, Category } from './types';
import api from './api/client';
import { ShoppingCart, User, Package, Home, LogOut, Info } from 'lucide-react';
import Login from './pages/Login';
import Register from './pages/Register';
import Cart from './pages/Cart';
import Checkout from './pages/Checkout';
import Orders from './pages/Orders';
import About from './pages/About';

function Header() {
  const navigate = useNavigate();
  const isLoggedIn = !!localStorage.getItem('client_token');
  const user = localStorage.getItem('client_user');
  const username = user ? JSON.parse(user).username : '';

  const handleLogout = () => {
    localStorage.removeItem('client_token');
    localStorage.removeItem('client_user');
    navigate('/');
  };

  return (
    <header className="bg-white/95 backdrop-blur-md shadow-lg sticky top-0 z-50 border-b border-gray-100">
      <div className="max-w-7xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <Link to="/" className="text-3xl font-extrabold bg-gradient-to-r from-red-600 to-orange-500 bg-clip-text text-transparent flex items-center gap-2 hover:scale-105 transition-transform">
            🍕 Food Delivery
          </Link>
          <nav className="flex gap-2 md:gap-4 items-center">
            <Link to="/" className="text-gray-700 hover:text-red-600 font-semibold flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-red-50 transition-all">
              <Home className="w-5 h-5" />
              <span className="hidden md:inline">Меню</span>
            </Link>
            <Link to="/about" className="text-gray-700 hover:text-red-600 font-semibold flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-red-50 transition-all">
              <Info className="w-5 h-5" />
              <span className="hidden md:inline">Про нас</span>
            </Link>
            <Link to="/cart" className="text-gray-700 hover:text-red-600 font-semibold flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-red-50 transition-all">
              <ShoppingCart className="w-5 h-5" />
              <span className="hidden md:inline">Кошик</span>
            </Link>
            {isLoggedIn ? (
              <>
                <Link to="/orders" className="text-gray-700 hover:text-red-600 font-semibold flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-red-50 transition-all">
                  <Package className="w-5 h-5" />
                  <span className="hidden md:inline">Замовлення</span>
                </Link>
                <div className="flex items-center gap-3 ml-2">
                  <span className="text-sm font-medium text-gray-700 bg-gray-100 px-3 py-1.5 rounded-full hidden md:inline">
                    {username}
                  </span>
                  <button
                    onClick={handleLogout}
                    className="text-gray-700 hover:text-red-600 font-semibold flex items-center gap-2 px-3 py-2 rounded-xl hover:bg-red-50 transition-all"
                  >
                    <LogOut className="w-5 h-5" />
                    <span className="hidden md:inline">Вихід</span>
                  </button>
                </div>
              </>
            ) : (
              <Link to="/login" className="bg-gradient-to-r from-red-600 to-red-500 text-white font-semibold px-5 py-2.5 rounded-xl hover:from-red-700 hover:to-red-600 transition-all flex items-center gap-2 shadow-md hover:shadow-lg">
                <User className="w-5 h-5" />
                <span className="hidden md:inline">Вхід</span>
              </Link>
            )}
          </nav>
        </div>
      </div>
    </header>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-gray-50">
        <Header />

        {/* Main Content */}
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/checkout" element={<Checkout />} />
            <Route path="/orders" element={<Orders />} />
            <Route path="/about" element={<About />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white mt-24">
          <div className="max-w-7xl mx-auto px-4 py-12">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-10 mb-8">
              {/* Про нас */}
              <div>
                <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                  Про нас
                </h3>
                <p className="text-gray-400 text-sm leading-relaxed">
                  Food Delivery - ваш надійний партнер у доставці смачної їжі швидко та зручно.
                </p>
              </div>
              
              {/* Навігація */}
              <div>
                <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                  Навігація
                </h3>
                <ul className="space-y-3 text-sm">
                  <li>
                    <Link to="/" className="text-gray-400 hover:text-white transition-colors flex items-center gap-2 group">
                      <span className="w-1 h-1 bg-red-500 rounded-full group-hover:w-2 transition-all"></span>
                      Меню
                    </Link>
                  </li>
                  <li>
                    <Link to="/about" className="text-gray-400 hover:text-white transition-colors flex items-center gap-2 group">
                      <span className="w-1 h-1 bg-red-500 rounded-full group-hover:w-2 transition-all"></span>
                      Про ресторан
                    </Link>
                  </li>
                  <li>
                    <Link to="/orders" className="text-gray-400 hover:text-white transition-colors flex items-center gap-2 group">
                      <span className="w-1 h-1 bg-red-500 rounded-full group-hover:w-2 transition-all"></span>
                      Мої замовлення
                    </Link>
                  </li>
                </ul>
              </div>
              
              {/* Соціальні мережі та контакти */}
              <div>
                <h3 className="text-xl font-bold mb-4 bg-gradient-to-r from-red-400 to-orange-400 bg-clip-text text-transparent">
                  Зв'яжіться з нами
                </h3>
                <div className="flex gap-4 mb-5">
                  <a 
                    href="https://facebook.com" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-10 h-10 bg-gray-700 hover:bg-blue-600 rounded-full flex items-center justify-center transition-all hover:scale-110"
                    aria-label="Facebook"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/>
                    </svg>
                  </a>
                  <a 
                    href="https://instagram.com" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-10 h-10 bg-gray-700 hover:bg-gradient-to-br hover:from-purple-600 hover:to-pink-500 rounded-full flex items-center justify-center transition-all hover:scale-110"
                    aria-label="Instagram"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zm0-2.163c-3.259 0-3.667.014-4.947.072-4.358.2-6.78 2.618-6.98 6.98-.059 1.281-.073 1.689-.073 4.948 0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98 1.281.058 1.689.072 4.948.072 3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98-1.281-.059-1.69-.073-4.949-.073zm0 5.838c-3.403 0-6.162 2.759-6.162 6.162s2.759 6.163 6.162 6.163 6.162-2.759 6.162-6.163c0-3.403-2.759-6.162-6.162-6.162zm0 10.162c-2.209 0-4-1.79-4-4 0-2.209 1.791-4 4-4s4 1.791 4 4c0 2.21-1.791 4-4 4zm6.406-11.845c-.796 0-1.441.645-1.441 1.44s.645 1.44 1.441 1.44c.795 0 1.439-.645 1.439-1.44s-.644-1.44-1.439-1.44z"/>
                    </svg>
                  </a>
                  <a 
                    href="https://twitter.com" 
                    target="_blank" 
                    rel="noopener noreferrer"
                    className="w-10 h-10 bg-gray-700 hover:bg-blue-400 rounded-full flex items-center justify-center transition-all hover:scale-110"
                    aria-label="Twitter"
                  >
                    <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                    </svg>
                  </a>
                </div>
                <p className="text-gray-400 text-sm mb-2 flex items-center gap-2">
                  <span>📞</span> +380 XX XXX XXXX
                </p>
                <p className="text-gray-400 text-sm flex items-center gap-2">
                  <span>📧</span> info@fooddelivery.com
                </p>
              </div>
            </div>
            
            <div className="border-t border-gray-700 pt-8 text-center">
              <p className="text-gray-400 text-sm">
                Food Delivery 2025 • Створено з ❤️ для любителів смачної їжі
              </p>
            </div>
          </div>
        </footer>
      </div>
    </BrowserRouter>
  );
}

// Home Page with Menu
function HomePage() {
  const [menuItems, setMenuItems] = useState<MenuItem[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);

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
      const response = await api.get('/menu/', { params });
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

  const addToCart = async (item: MenuItem) => {
    // Check if user is logged in
    if (!localStorage.getItem('client_token')) {
      if (confirm('Для додавання в кошик потрібно увійти. Перейти на сторінку входу?')) {
        window.location.href = '/login';
      }
      return;
    }

    try {
      await api.post('/cart/me/items', {
        menu_item_id: item.id,
        quantity: 1,
        price: item.price,
      });
      
      // Remove existing notifications to avoid stacking
      const existingNotifications = document.querySelectorAll('.cart-notification');
      existingNotifications.forEach(n => n.remove());
      
      // Show success message with modern design
      const notification = document.createElement('div');
      notification.className = 'cart-notification fixed top-24 right-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white px-6 py-4 rounded-2xl shadow-2xl z-50 animate-fade-in flex items-center gap-3 max-w-md';
      notification.innerHTML = `
        <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path>
          </svg>
        </div>
        <div>
          <p class="font-bold">${item.name}</p>
          <p class="text-sm text-green-100">успішно додано в кошик</p>
        </div>
      `;
      document.body.appendChild(notification);
      
      setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(400px)';
        notification.style.transition = 'all 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
      }, 3000);
    } catch (error) {
      console.error('Failed to add to cart:', error);
      
      // Remove existing notifications
      const existingNotifications = document.querySelectorAll('.cart-notification');
      existingNotifications.forEach(n => n.remove());
      
      // Show error message
      const notification = document.createElement('div');
      notification.className = 'cart-notification fixed top-24 right-4 bg-gradient-to-r from-red-500 to-rose-500 text-white px-6 py-4 rounded-2xl shadow-2xl z-50 animate-fade-in flex items-center gap-3';
      notification.innerHTML = `
        <div class="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center flex-shrink-0">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
          </svg>
        </div>
        <div>
          <p class="font-bold">Помилка</p>
          <p class="text-sm text-red-100">Не вдалося додати в кошик</p>
        </div>
      `;
      document.body.appendChild(notification);
      
      setTimeout(() => {
        notification.style.opacity = '0';
        notification.style.transform = 'translateX(400px)';
        notification.style.transition = 'all 0.3s ease-out';
        setTimeout(() => notification.remove(), 300);
      }, 3000);
    }
  };

  return (
    <div className="bg-gradient-to-b from-gray-50 to-white min-h-screen">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-red-600 via-red-500 to-orange-500 text-white">
        <div className="max-w-7xl mx-auto px-4 py-16 md:py-20">
          <div className="text-center">
            <h1 className="text-5xl md:text-6xl font-extrabold mb-4 tracking-tight">
              Смачна їжа до вашого дому
            </h1>
            <p className="text-xl md:text-2xl text-red-50 max-w-2xl mx-auto">
              Обирайте з нашого меню та насолоджуйтесь швидкою доставкою
            </p>
          </div>
        </div>
      </div>

      {/* Menu Section */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Category Filter */}
        {categories.length > 0 && (
          <div className="mb-10">
            <div className="flex gap-3 overflow-x-auto pb-3 scrollbar-hide">
              <button
                onClick={() => handleCategoryClick(null)}
                className={`px-6 py-3 rounded-2xl font-semibold transition-all whitespace-nowrap flex-shrink-0 ${
                  selectedCategory === null
                    ? 'bg-gradient-to-r from-red-600 to-red-500 text-white shadow-lg shadow-red-500/30 scale-105'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200 hover:border-red-300'
                }`}
              >
                Всі страви
              </button>
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => handleCategoryClick(category.id)}
                  className={`px-6 py-3 rounded-2xl font-semibold transition-all whitespace-nowrap flex-shrink-0 ${
                    selectedCategory === category.id
                      ? 'bg-gradient-to-r from-red-600 to-red-500 text-white shadow-lg shadow-red-500/30 scale-105'
                      : 'bg-white text-gray-700 hover:bg-gray-50 border-2 border-gray-200 hover:border-red-300'
                  }`}
                >
                  {category.name}
                </button>
              ))}
            </div>
          </div>
        )}

        {loading ? (
          <div className="flex justify-center p-20">
            <div className="relative">
              <div className="animate-spin rounded-full h-20 w-20 border-t-4 border-b-4 border-red-600"></div>
              <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 text-3xl">
                🍕
              </div>
            </div>
          </div>
        ) : menuItems.length === 0 ? (
          <div className="text-center py-20 bg-white rounded-3xl shadow-sm">
            <div className="text-6xl mb-4">😔</div>
            <p className="text-gray-500 text-xl mb-2 font-medium">Меню тимчасово недоступне</p>
            <p className="text-gray-400">Будь ласка, зайдіть пізніше</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            {menuItems.map((item) => (
              <div 
                key={item.id} 
                className="group bg-white rounded-3xl shadow-md hover:shadow-2xl transition-all duration-300 overflow-hidden transform hover:-translate-y-2 flex flex-col"
              >
                <div className="relative overflow-hidden">
                  {item.image_url ? (
                    <img 
                      src={item.image_url} 
                      alt={item.name} 
                      className="w-full h-56 object-cover group-hover:scale-110 transition-transform duration-500"
                    />
                  ) : (
                    <div className="w-full h-56 bg-gradient-to-br from-red-400 via-orange-400 to-yellow-400 flex items-center justify-center">
                      <span className="text-white text-7xl drop-shadow-lg">🍕</span>
                    </div>
                  )}
                  {/* Price badge */}
                  <div className="absolute top-4 right-4 bg-white/95 backdrop-blur-sm px-4 py-2 rounded-full shadow-lg">
                    <span className="text-2xl font-bold text-red-600">
                      ₴{(item.price / 100).toFixed(0)}
                    </span>
                  </div>
                </div>
                
                <div className="p-6 flex flex-col flex-1">
                  <h3 className="text-2xl font-bold text-gray-900 mb-3 group-hover:text-red-600 transition-colors">
                    {item.name}
                  </h3>
                  <p className="text-gray-600 mb-5 text-sm leading-relaxed line-clamp-2 flex-1">
                    {item.description || 'Смачна страва від нашого кухаря'}
                  </p>
                  <button 
                    onClick={() => addToCart(item)}
                    className="w-full bg-gradient-to-r from-red-600 to-red-500 text-white px-6 py-3.5 rounded-xl hover:from-red-700 hover:to-red-600 transition-all font-semibold flex items-center justify-center gap-2 shadow-lg shadow-red-500/25 hover:shadow-xl hover:shadow-red-500/40 active:scale-95"
                  >
                    <ShoppingCart className="w-5 h-5" />
                    Додати в кошик
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
