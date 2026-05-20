import { Link } from 'react-router-dom';
import { Home } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="min-h-screen bg-neutral-100 dark:bg-neutral-800 flex items-center justify-center p-4">
      <div className="text-center">
        <h1 className="text-9xl font-black text-neutral-900 dark:text-white tracking-tighter">404</h1>
        <div className="w-24 h-1.5 bg-gradient-to-r from-neutral-900 via-neutral-700 to-neutral-900 mx-auto my-6 rounded-full"></div>
        <p className="text-2xl font-bold text-neutral-700 dark:text-neutral-300 mb-2">Сторінку не знайдено</p>
        <p className="text-neutral-500 dark:text-neutral-400 mb-8">
          Сторінка, яку ви шукаєте, не існує або була переміщена
        </p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 bg-neutral-900 dark:bg-white text-white dark:text-black px-6 py-3 rounded-xl hover:bg-neutral-800 dark:hover:bg-neutral-200 transition-colors font-semibold text-sm shadow-lg"
        >
          <Home className="w-4 h-4" />
          Повернутися на головну
        </Link>
      </div>
    </div>
  );
}
