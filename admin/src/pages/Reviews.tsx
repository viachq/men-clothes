import { useEffect, useState } from 'react';
import api from '../api/client';
import type { Review } from '../types';
import { Trash2, Star } from 'lucide-react';

export default function Reviews() {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchReviews();
  }, []);

  const fetchReviews = async () => {
    try {
      const response = await api.get('/reviews/');
      setReviews(response.data);
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: number) => {
    if (!confirm('Delete this review?')) return;
    try {
      await api.delete(`/reviews/${id}`);
      fetchReviews();
    } catch (error) {
      console.error('Failed to delete review:', error);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">Reviews Management</h1>
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12">
          <div className="flex flex-col items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600 mb-4"></div>
            <p className="text-gray-500 font-medium">Loading reviews...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Reviews Management</h1>

      {reviews.length === 0 ? (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-12">
          <div className="flex flex-col items-center justify-center text-center">
            <Star className="w-16 h-16 text-gray-300 mb-4" />
            <p className="text-gray-500 text-lg font-medium">No reviews yet</p>
            <p className="text-gray-400 text-sm mt-2">Customer reviews will appear here after they rate their delivered orders</p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {reviews.map((review) => (
          <div key={review.id} className="bg-white rounded-xl shadow-sm border p-6">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <div className="flex">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className={`w-5 h-5 ${i < review.rating ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300'}`}
                      />
                    ))}
                  </div>
                  <span className="text-sm text-gray-500">by User #{review.user_id}</span>
                </div>
                <p className="text-gray-700 mb-2">{review.text}</p>
                <p className="text-xs text-gray-500">{new Date(review.created_at).toLocaleString()}</p>
              </div>
              <button
                onClick={() => handleDelete(review.id)}
                className="p-2 text-red-600 hover:bg-red-50 rounded-lg ml-4"
              >
                <Trash2 className="w-5 h-5" />
              </button>
            </div>
          </div>
          ))}
        </div>
      )}
    </div>
  );
}

