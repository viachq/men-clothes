import { useEffect, useState } from 'react';
import api from '../api/client';
import type { MenuItem } from '../types';
import { MessageSquare, Star, Trash2, ChevronDown } from 'lucide-react';

interface Review {
  id: number;
  user_id: number;
  username: string;
  product_id: number;
  rating: number;
  comment: string;
  created_at: string;
}

export default function Reviews() {
  const [products, setProducts] = useState<MenuItem[]>([]);
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [reviewsLoading, setReviewsLoading] = useState(false);

  useEffect(() => {
    fetchProducts();
  }, []);

  useEffect(() => {
    if (selectedProductId) {
      fetchReviews(selectedProductId);
    } else {
      setReviews([]);
    }
  }, [selectedProductId]);

  const fetchProducts = async () => {
    try {
      const response = await api.get('/products/');
      setProducts(response.data);
    } catch (error) {
      console.error('Failed to fetch products:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchReviews = async (productId: number) => {
    setReviewsLoading(true);
    try {
      const response = await api.get(`/reviews/product/${productId}`);
      setReviews(response.data);
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
      setReviews([]);
    } finally {
      setReviewsLoading(false);
    }
  };

  const handleDelete = async (reviewId: number) => {
    if (!confirm('Видалити цей відгук?')) return;
    try {
      await api.delete(`/reviews/${reviewId}`);
      if (selectedProductId) {
        fetchReviews(selectedProductId);
      }
    } catch (error) {
      console.error('Failed to delete review:', error);
    }
  };

  const averageRating =
    reviews.length > 0
      ? reviews.reduce((sum, r) => sum + r.rating, 0) / reviews.length
      : 0;

  const renderStars = (rating: number) => {
    return (
      <div className="flex items-center gap-0.5">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating
                ? 'fill-yellow-400 text-yellow-400'
                : 'fill-neutral-200 text-neutral-200 dark:fill-neutral-700 dark:text-neutral-700'
            }`}
          />
        ))}
      </div>
    );
  };

  const selectedProduct = products.find((p) => p.id === selectedProductId);

  if (loading) {
    return (
      <div className="flex justify-center p-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900 dark:border-white"></div>
      </div>
    );
  }

  return (
    <div className="max-w-[1600px] mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between border-b-2 border-neutral-200 dark:border-neutral-700 pb-4">
        <div className="flex items-center gap-3">
          <MessageSquare className="w-6 h-6 text-neutral-900 dark:text-white" />
          <h1 className="text-2xl font-black text-neutral-900 dark:text-white tracking-tight uppercase">
            Відгуки
          </h1>
        </div>
      </div>

      {/* Product selector */}
      <div className="bg-white dark:bg-neutral-900 rounded-2xl p-6 border-2 border-neutral-200 dark:border-neutral-700 shadow-sm">
        <label className="block text-xs font-bold text-neutral-600 dark:text-neutral-400 uppercase tracking-wider mb-3">
          Оберіть товар
        </label>
        <div className="relative">
          <select
            value={selectedProductId || ''}
            onChange={(e) =>
              setSelectedProductId(e.target.value ? Number(e.target.value) : null)
            }
            className="w-full px-4 py-3.5 bg-neutral-50 dark:bg-neutral-800 border-2 border-neutral-200 dark:border-neutral-600 rounded-xl focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white focus:border-neutral-900 dark:focus:border-white transition-all font-medium text-neutral-900 dark:text-white appearance-none cursor-pointer"
          >
            <option value="">-- Оберіть товар для перегляду відгуків --</option>
            {products.map((product) => (
              <option key={product.id} value={product.id}>
                {product.name}
              </option>
            ))}
          </select>
          <ChevronDown className="absolute right-4 top-1/2 -translate-y-1/2 w-5 h-5 text-neutral-400 dark:text-neutral-500 pointer-events-none" />
        </div>
      </div>

      {/* Stats bar */}
      {selectedProductId && !reviewsLoading && (
        <div className="flex items-center gap-6 bg-white dark:bg-neutral-900 rounded-2xl p-6 border-2 border-neutral-200 dark:border-neutral-700 shadow-sm">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 bg-neutral-100 dark:bg-neutral-800 rounded-xl flex items-center justify-center">
              <Star className="w-6 h-6 fill-yellow-400 text-yellow-400" />
            </div>
            <div>
              <p className="text-3xl font-black text-neutral-900 dark:text-white">
                {averageRating.toFixed(1)}
              </p>
              <p className="text-xs font-medium text-neutral-500 dark:text-neutral-400">Середня оцінка</p>
            </div>
          </div>
          <div className="w-px h-12 bg-neutral-200 dark:bg-neutral-700"></div>
          <div>
            <p className="text-3xl font-black text-neutral-900 dark:text-white">{reviews.length}</p>
            <p className="text-xs font-medium text-neutral-500 dark:text-neutral-400">
              {reviews.length === 1 ? 'Відгук' : 'Відгуків'}
            </p>
          </div>
          {selectedProduct && (
            <>
              <div className="w-px h-12 bg-neutral-200 dark:bg-neutral-700"></div>
              <div>
                <p className="text-sm font-bold text-neutral-900 dark:text-white">{selectedProduct.name}</p>
                <p className="text-xs font-medium text-neutral-500 dark:text-neutral-400">Обраний товар</p>
              </div>
            </>
          )}
        </div>
      )}

      {/* Reviews list */}
      {!selectedProductId ? (
        <div className="bg-white dark:bg-neutral-900 rounded-2xl border-2 border-neutral-200 dark:border-neutral-700 shadow-sm py-16 text-center">
          <MessageSquare className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
          <p className="text-neutral-500 dark:text-neutral-400 text-lg font-semibold">Оберіть товар</p>
          <p className="text-neutral-400 dark:text-neutral-500 text-sm mt-2">
            Оберіть товар зі списку, щоб переглянути його відгуки
          </p>
        </div>
      ) : reviewsLoading ? (
        <div className="flex justify-center p-8">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900 dark:border-white"></div>
        </div>
      ) : reviews.length === 0 ? (
        <div className="bg-white dark:bg-neutral-900 rounded-2xl border-2 border-neutral-200 dark:border-neutral-700 shadow-sm py-16 text-center">
          <Star className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
          <p className="text-neutral-500 dark:text-neutral-400 text-lg font-semibold">Відгуків немає</p>
          <p className="text-neutral-400 dark:text-neutral-500 text-sm mt-2">
            Для цього товару ще немає жодного відгуку
          </p>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
            <div
              key={review.id}
              className="bg-white dark:bg-neutral-900 rounded-2xl border-2 border-neutral-200 dark:border-neutral-700 shadow-sm p-6 hover:border-neutral-300 dark:hover:border-neutral-600 transition-all"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-3">
                    <div className="w-9 h-9 bg-neutral-900 rounded-full flex items-center justify-center">
                      <span className="text-white text-sm font-bold">
                        {review.username?.charAt(0).toUpperCase() || 'U'}
                      </span>
                    </div>
                    <div>
                      <p className="text-sm font-bold text-neutral-900 dark:text-white">
                        {review.username || `User #${review.user_id}`}
                      </p>
                      <p className="text-xs text-neutral-500 dark:text-neutral-400">
                        {new Date(review.created_at).toLocaleDateString('uk-UA', {
                          year: 'numeric',
                          month: 'long',
                          day: 'numeric',
                        })}
                      </p>
                    </div>
                  </div>

                  <div className="mb-3">{renderStars(review.rating)}</div>

                  {review.comment && (
                    <p className="text-sm text-neutral-700 dark:text-neutral-300 leading-relaxed">{review.comment}</p>
                  )}
                </div>

                <button
                  onClick={() => handleDelete(review.id)}
                  className="ml-4 p-2 text-neutral-400 dark:text-neutral-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-all"
                  title="Видалити відгук"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
