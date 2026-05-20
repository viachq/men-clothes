import { useEffect, useState } from 'react';
import { X, Star, ShoppingCart, Send, Trash2 } from 'lucide-react';
import type { MenuItem, Review, ProductVariant } from '../types';
import api from '../api/client';
import { showSuccess, showError } from '../utils/notifications';

interface ProductModalProps {
  product: MenuItem;
  onClose: () => void;
  onAddToCart: (item: MenuItem) => void;
}

export default function ProductModal({ product, onClose, onAddToCart }: ProductModalProps) {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [canReview, setCanReview] = useState(false);
  const [rating, setRating] = useState(5);
  const [hoverRating, setHoverRating] = useState(0);
  const [comment, setComment] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [loadingReviews, setLoadingReviews] = useState(true);
  const [variants, setVariants] = useState<ProductVariant[]>([]);
  const [selectedSize, setSelectedSize] = useState<string | null>(null);
  const [loadingVariants, setLoadingVariants] = useState(true);
  const isLoggedIn = !!localStorage.getItem('client_token');
  const currentUser = localStorage.getItem('client_user');
  const currentUserId = currentUser ? JSON.parse(currentUser).id : null;

  useEffect(() => {
    fetchReviews();
    fetchVariants();
    if (isLoggedIn) checkCanReview();
    document.body.style.overflow = 'hidden';
    return () => { document.body.style.overflow = ''; };
  }, [product.id]);

  const fetchVariants = async () => {
    setLoadingVariants(true);
    try {
      const res = await api.get(`/variants/product/${product.id}`);
      setVariants(res.data);
    } catch {
      // ignore - variants may not exist
    } finally {
      setLoadingVariants(false);
    }
  };

  const selectedVariant = variants.find((v) => v.size === selectedSize);
  const hasVariants = variants.length > 0;
  const isAddDisabled = hasVariants && (!selectedSize || !selectedVariant || selectedVariant.stock <= 0);

  useEffect(() => {
    const handleEsc = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handleEsc);
    return () => window.removeEventListener('keydown', handleEsc);
  }, [onClose]);

  const fetchReviews = async () => {
    try {
      const res = await api.get(`/reviews/product/${product.id}`);
      setReviews(res.data);
    } catch {
      // ignore
    } finally {
      setLoadingReviews(false);
    }
  };

  const checkCanReview = async () => {
    try {
      const res = await api.get(`/reviews/can-review/${product.id}`);
      setCanReview(res.data.can_review);
    } catch {
      // ignore
    }
  };

  const submitReview = async (e: React.FormEvent) => {
    e.preventDefault();
    setSubmitting(true);
    try {
      await api.post(`/reviews/product/${product.id}`, { rating, comment: comment.trim() || null });
      showSuccess('Відгук додано!');
      setComment('');
      setCanReview(false);
      fetchReviews();
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Не вдалося додати відгук');
    } finally {
      setSubmitting(false);
    }
  };

  const deleteReview = async (reviewId: number) => {
    try {
      await api.delete(`/reviews/${reviewId}`);
      showSuccess('Відгук видалено');
      fetchReviews();
      setCanReview(true);
    } catch {
      showError('Не вдалося видалити відгук');
    }
  };

  const avgRating = reviews.length > 0
    ? reviews.reduce((s, r) => s + r.rating, 0) / reviews.length
    : 0;

  return (
    <div className="fixed inset-0 z-[100] flex items-center justify-center p-4" onClick={onClose}>
      <div className="absolute inset-0 bg-black/50 backdrop-blur-sm" />
      <div
        className="relative bg-white dark:bg-neutral-900 w-full max-w-3xl max-h-[90vh] overflow-y-auto rounded-sm shadow-2xl animate-scale-in"
        onClick={(e) => e.stopPropagation()}
      >
        <button
          onClick={onClose}
          className="absolute top-4 right-4 z-10 p-2 bg-white/80 dark:bg-neutral-800/80 backdrop-blur-sm rounded-full hover:bg-neutral-100 dark:hover:bg-neutral-700 transition-colors"
        >
          <X className="w-5 h-5 dark:text-white" />
        </button>

        <div className="grid grid-cols-1 md:grid-cols-2">
          {/* Image */}
          <div className="relative aspect-square bg-neutral-100 dark:bg-neutral-800">
            {product.badge && (
              <span className={`absolute top-4 left-4 z-10 px-3 py-1.5 text-xs font-black uppercase tracking-wider text-white ${
                product.badge === 'sale' ? 'bg-red-500' : 'bg-black'
              }`}>
                {product.badge === 'sale' ? 'Sale' : 'New'}
              </span>
            )}
            {product.image_url ? (
              <img src={product.image_url} alt={product.name} className="w-full h-full object-cover" />
            ) : (
              <div className="w-full h-full flex items-center justify-center text-8xl text-neutral-200 dark:text-neutral-600">
                👔
              </div>
            )}
          </div>

          {/* Details */}
          <div className="p-6 md:p-8 flex flex-col">
            <h2 className="text-xl md:text-2xl font-black text-black dark:text-white tracking-tight mb-2">
              {product.name}
            </h2>

            {reviews.length > 0 && (
              <div className="flex items-center gap-2 mb-3">
                <div className="flex">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <Star
                      key={s}
                      className={`w-4 h-4 ${s <= Math.round(avgRating) ? 'text-yellow-400 fill-yellow-400' : 'text-neutral-200 dark:text-neutral-600'}`}
                    />
                  ))}
                </div>
                <span className="text-sm text-neutral-500 dark:text-neutral-400">
                  {avgRating.toFixed(1)} ({reviews.length})
                </span>
              </div>
            )}

            <div className="flex items-baseline gap-3 mb-4">
              <span className={`text-2xl md:text-3xl font-black ${product.old_price ? 'text-red-600' : 'text-black dark:text-white'}`}>
                ₴{(product.price / 100).toFixed(0)}
              </span>
              {product.old_price && (
                <span className="text-lg md:text-xl text-neutral-400 dark:text-neutral-500 line-through font-medium">
                  ₴{(product.old_price / 100).toFixed(0)}
                </span>
              )}
              {product.old_price && (
                <span className="text-sm font-bold text-red-500">
                  -{Math.round((1 - product.price / product.old_price) * 100)}%
                </span>
              )}
            </div>

            {product.description && (
              <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed mb-6">
                {product.description}
              </p>
            )}

            {/* Size Selector */}
            {!loadingVariants && hasVariants && (
              <div className="mb-5">
                <p className="text-xs font-bold text-black dark:text-white uppercase tracking-[0.15em] mb-3">
                  Розмір
                </p>
                <div className="flex gap-2 flex-wrap">
                  {variants.map((variant) => {
                    const outOfStock = variant.stock <= 0;
                    const isSelected = selectedSize === variant.size;
                    return (
                      <button
                        key={variant.id}
                        type="button"
                        disabled={outOfStock}
                        onClick={() => setSelectedSize(isSelected ? null : variant.size)}
                        className={`px-4 py-2 text-sm font-semibold border transition-all duration-200 uppercase tracking-wide ${
                          outOfStock
                            ? 'border-neutral-100 dark:border-neutral-800 text-neutral-300 dark:text-neutral-600 bg-neutral-50 dark:bg-neutral-800 cursor-not-allowed line-through'
                            : isSelected
                            ? 'border-black dark:border-white bg-black dark:bg-white text-white dark:text-black'
                            : 'border-neutral-300 dark:border-neutral-600 text-neutral-700 dark:text-neutral-300 hover:border-black dark:hover:border-white hover:text-black dark:hover:text-white bg-white dark:bg-neutral-900'
                        }`}
                      >
                        {variant.size}
                      </button>
                    );
                  })}
                </div>
                {selectedVariant && selectedVariant.stock > 0 && (
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mt-2">
                    В наявності: {selectedVariant.stock} шт
                  </p>
                )}
                {selectedVariant && selectedVariant.stock <= 0 && (
                  <p className="text-xs text-red-500 mt-2">
                    Немає в наявності
                  </p>
                )}
              </div>
            )}

            <button
              onClick={() => { onAddToCart(product); onClose(); }}
              disabled={isAddDisabled}
              className="w-full bg-black dark:bg-white text-white dark:text-black py-3.5 font-bold text-sm uppercase tracking-wider hover:bg-neutral-800 dark:hover:bg-neutral-200 disabled:opacity-40 disabled:cursor-not-allowed transition-colors flex items-center justify-center gap-2 mt-auto"
            >
              <ShoppingCart className="w-4 h-4" />
              {hasVariants && !selectedSize ? 'Оберіть розмір' : 'Додати в кошик'}
            </button>
          </div>
        </div>

        {/* Reviews Section */}
        <div className="border-t border-neutral-200 dark:border-neutral-700 p-6 md:p-8">
          <h3 className="text-lg font-black text-black dark:text-white uppercase tracking-wide mb-6">
            Відгуки {reviews.length > 0 && `(${reviews.length})`}
          </h3>

          {/* Write Review Form */}
          {isLoggedIn && canReview && (
            <form onSubmit={submitReview} className="mb-8 p-4 bg-neutral-50 dark:bg-neutral-800 rounded-sm">
              <p className="text-sm font-semibold text-black dark:text-white mb-3">Залишити відгук</p>
              <div className="flex gap-1 mb-3">
                {[1, 2, 3, 4, 5].map((s) => (
                  <button
                    key={s}
                    type="button"
                    onClick={() => setRating(s)}
                    onMouseEnter={() => setHoverRating(s)}
                    onMouseLeave={() => setHoverRating(0)}
                    className="p-0.5 transition-transform hover:scale-110"
                  >
                    <Star
                      className={`w-6 h-6 transition-colors ${
                        s <= (hoverRating || rating)
                          ? 'text-yellow-400 fill-yellow-400'
                          : 'text-neutral-300 dark:text-neutral-600'
                      }`}
                    />
                  </button>
                ))}
              </div>
              <textarea
                value={comment}
                onChange={(e) => setComment(e.target.value)}
                placeholder="Ваш коментар (необов'язково)..."
                maxLength={2000}
                rows={3}
                className="w-full px-3 py-2 text-sm border border-neutral-200 dark:border-neutral-700 rounded-sm focus:border-black dark:focus:border-white focus:outline-none resize-none mb-3 bg-white dark:bg-neutral-900 dark:text-white"
              />
              <button
                type="submit"
                disabled={submitting}
                className="bg-black dark:bg-white text-white dark:text-black px-5 py-2 text-xs font-bold uppercase tracking-wider hover:bg-neutral-800 dark:hover:bg-neutral-200 disabled:opacity-50 transition-colors flex items-center gap-2"
              >
                <Send className="w-3.5 h-3.5" />
                {submitting ? 'Надсилання...' : 'Надіслати'}
              </button>
            </form>
          )}

          {/* Reviews List */}
          {loadingReviews ? (
            <div className="space-y-4">
              {[1, 2].map((i) => (
                <div key={i} className="animate-pulse">
                  <div className="h-4 bg-neutral-100 dark:bg-neutral-800 rounded w-1/3 mb-2" />
                  <div className="h-3 bg-neutral-100 dark:bg-neutral-800 rounded w-2/3" />
                </div>
              ))}
            </div>
          ) : reviews.length === 0 ? (
            <p className="text-sm text-neutral-400 dark:text-neutral-500 text-center py-8">
              Ще немає відгуків. Будьте першим!
            </p>
          ) : (
            <div className="space-y-4">
              {reviews.map((review) => (
                <div key={review.id} className="border-b border-neutral-100 dark:border-neutral-800 pb-4 last:border-0">
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-semibold text-black dark:text-white">{review.username}</span>
                      <div className="flex">
                        {[1, 2, 3, 4, 5].map((s) => (
                          <Star
                            key={s}
                            className={`w-3.5 h-3.5 ${
                              s <= review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-neutral-200 dark:text-neutral-600'
                            }`}
                          />
                        ))}
                      </div>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-xs text-neutral-400 dark:text-neutral-500">
                        {new Date(review.created_at).toLocaleDateString('uk-UA')}
                      </span>
                      {currentUserId === review.user_id && (
                        <button
                          onClick={() => deleteReview(review.id)}
                          className="p-1 text-neutral-300 dark:text-neutral-600 hover:text-red-500 dark:hover:text-red-400 transition-colors"
                          title="Видалити відгук"
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                        </button>
                      )}
                    </div>
                  </div>
                  {review.comment && (
                    <p className="text-sm text-neutral-600 dark:text-neutral-400 leading-relaxed">{review.comment}</p>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
