import { Link } from 'react-router-dom';
import { Phone, Mail, MapPin, Instagram, Facebook, Twitter } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-neutral-900 dark:bg-neutral-950 border-t border-neutral-800 dark:border-neutral-800 mt-20 md:mt-24 text-neutral-300">
      <div className="max-w-[1920px] mx-auto px-6 md:px-12 lg:px-16 xl:px-20">
        {/* Main Footer Grid */}
        <div className="py-12 md:py-16 grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-10 lg:gap-12">
          {/* Column 1 - Company Info */}
          <div className="sm:col-span-2 lg:col-span-1">
            <Link
              to="/"
              className="inline-block text-lg font-black text-white tracking-[0.08em] uppercase hover:opacity-70 transition-opacity duration-200 mb-4"
            >
              Men's Clothes
            </Link>
            <p className="text-sm leading-relaxed text-neutral-400 mb-6 max-w-xs">
              Інтернет-магазин чоловічого одягу преміум якості. Стиль, комфорт та сучасний дизайн для кожного чоловіка.
            </p>
            {/* Social Icons */}
            <div className="flex items-center gap-3">
              <a
                href="#"
                aria-label="Instagram"
                className="w-9 h-9 rounded-full border border-neutral-700 flex items-center justify-center text-neutral-400 hover:text-white hover:border-white transition-all duration-200"
              >
                <Instagram className="w-4 h-4" />
              </a>
              <a
                href="#"
                aria-label="Facebook"
                className="w-9 h-9 rounded-full border border-neutral-700 flex items-center justify-center text-neutral-400 hover:text-white hover:border-white transition-all duration-200"
              >
                <Facebook className="w-4 h-4" />
              </a>
              <a
                href="#"
                aria-label="Twitter"
                className="w-9 h-9 rounded-full border border-neutral-700 flex items-center justify-center text-neutral-400 hover:text-white hover:border-white transition-all duration-200"
              >
                <Twitter className="w-4 h-4" />
              </a>
            </div>
          </div>

          {/* Column 2 - Quick Links */}
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-[0.15em] mb-5">
              Навігація
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  to="/"
                  className="text-sm text-neutral-400 hover:text-white transition-colors duration-200"
                >
                  Каталог
                </Link>
              </li>
              <li>
                <Link
                  to="/cart"
                  className="text-sm text-neutral-400 hover:text-white transition-colors duration-200"
                >
                  Кошик
                </Link>
              </li>
              <li>
                <Link
                  to="/orders"
                  className="text-sm text-neutral-400 hover:text-white transition-colors duration-200"
                >
                  Мої замовлення
                </Link>
              </li>
              <li>
                <Link
                  to="/profile"
                  className="text-sm text-neutral-400 hover:text-white transition-colors duration-200"
                >
                  Профіль
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 3 - Info Links */}
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-[0.15em] mb-5">
              Інформація
            </h3>
            <ul className="space-y-3">
              <li>
                <Link
                  to="/about"
                  className="text-sm text-neutral-400 hover:text-white transition-colors duration-200"
                >
                  Про нас
                </Link>
              </li>
              <li>
                <Link
                  to="/contacts"
                  className="text-sm text-neutral-400 hover:text-white transition-colors duration-200"
                >
                  Контакти
                </Link>
              </li>
            </ul>
          </div>

          {/* Column 4 - Contact Info */}
          <div>
            <h3 className="text-xs font-bold text-white uppercase tracking-[0.15em] mb-5">
              Контакти
            </h3>
            <ul className="space-y-4">
              <li>
                <a
                  href="tel:+380441234567"
                  className="flex items-start gap-3 text-sm text-neutral-400 hover:text-white transition-colors duration-200 group"
                >
                  <Phone className="w-4 h-4 mt-0.5 flex-shrink-0 text-neutral-500 group-hover:text-white transition-colors duration-200" />
                  <span>+380 44 123 4567</span>
                </a>
              </li>
              <li>
                <a
                  href="mailto:info@mensclothes.ua"
                  className="flex items-start gap-3 text-sm text-neutral-400 hover:text-white transition-colors duration-200 group"
                >
                  <Mail className="w-4 h-4 mt-0.5 flex-shrink-0 text-neutral-500 group-hover:text-white transition-colors duration-200" />
                  <span>info@mensclothes.ua</span>
                </a>
              </li>
              <li>
                <div className="flex items-start gap-3 text-sm text-neutral-400">
                  <MapPin className="w-4 h-4 mt-0.5 flex-shrink-0 text-neutral-500" />
                  <span>вул. Хрещатик, 1, Київ, Україна</span>
                </div>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-neutral-800 py-6 flex flex-col sm:flex-row items-center justify-between gap-4">
          <p className="text-xs text-neutral-500 uppercase tracking-wide">
            &copy; 2025 Men's Clothes. Всі права захищені.
          </p>
          <div className="flex items-center gap-4">
            <span className="text-xs text-neutral-500 uppercase tracking-wide">Visa</span>
            <span className="text-xs text-neutral-600">|</span>
            <span className="text-xs text-neutral-500 uppercase tracking-wide">Mastercard</span>
            <span className="text-xs text-neutral-600">|</span>
            <span className="text-xs text-neutral-500 uppercase tracking-wide">Apple Pay</span>
          </div>
        </div>
      </div>
    </footer>
  );
}
