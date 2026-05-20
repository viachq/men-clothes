import { Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';

export default function NotFound() {
  return (
    <div className="max-w-3xl mx-auto p-8">
      <div className="text-center py-24">
        <p className="text-8xl font-black text-neutral-200 dark:text-neutral-700 mb-4">404</p>
        <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white mb-3 uppercase tracking-wide">
          Сторінку не знайдено
        </h1>
        <p className="text-neutral-600 dark:text-neutral-400 mb-8 text-sm">
          Сторінка, яку ви шукаєте, не існує або була переміщена.
        </p>
        <Link
          to="/"
          className="inline-flex items-center gap-2 bg-black dark:bg-white text-white dark:text-black px-6 py-3 text-sm font-bold uppercase tracking-wider hover:bg-neutral-800 dark:hover:bg-neutral-200 transition-colors"
        >
          <ArrowLeft className="w-5 h-5" />
          На головну
        </Link>
      </div>
    </div>
  );
}
