import { useEffect, useState } from 'react';
import { MapPin, Phone, Clock, Star, Mail } from 'lucide-react';
import api from '../api/client';

interface RestaurantInfo {
  id: number;
  name: string;
  description: string;
  address: string;
  phone: string;
  opening_hours: string;
}

interface Review {
  id: number;
  user_id: number;
  order_id: number;
  rating: number;
  text: string;
  created_at: string;
}

export default function About() {
  const [restaurantInfo, setRestaurantInfo] = useState<RestaurantInfo | null>(null);
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRestaurantInfo();
    fetchReviews();
  }, []);

  const fetchRestaurantInfo = async () => {
    try {
      const response = await api.get('/restaurant/info');
      setRestaurantInfo(response.data);
    } catch (error) {
      console.error('Failed to fetch restaurant info:', error);
    }
  };

  const fetchReviews = async () => {
    try {
      const response = await api.get('/restaurant/reviews');
      setReviews(response.data);
    } catch (error) {
      console.error('Failed to fetch reviews:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderStars = (rating: number) => {
    return (
      <div className="flex gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-5 h-5 ${
              star <= rating ? 'fill-yellow-400 text-yellow-400' : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  const calculateAverageRating = () => {
    if (reviews.length === 0) return 0;
    const sum = reviews.reduce((acc, review) => acc + review.rating, 0);
    return (sum / reviews.length).toFixed(1);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-red-600"></div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-red-600 to-orange-500 rounded-2xl p-8 md:p-12 text-white mb-12">
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          {restaurantInfo?.name || 'Food Delivery'}
        </h1>
        <p className="text-lg md:text-xl max-w-3xl opacity-95">
          {restaurantInfo?.description || 'Ваш надійний партнер у доставці смачної їжі'}
        </p>
      </div>

      {/* Contact Information */}
      <div className="bg-white rounded-xl shadow-md p-8 mb-12">
        <h2 className="text-3xl font-bold text-gray-900 mb-8 text-center">Контактна інформація</h2>
        
        <div className="grid md:grid-cols-2 gap-6 max-w-3xl mx-auto">
          <div className="flex items-start gap-3">
            <MapPin className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
            <div>
              <p className="font-medium text-gray-900">Адреса</p>
              <p className="text-gray-600">
                {restaurantInfo?.address || 'вул. Прикладна, 1, Київ, 01001'}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Phone className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
            <div>
              <p className="font-medium text-gray-900">Телефон</p>
              <p className="text-gray-600">
                {restaurantInfo?.phone || '+380 XX XXX XXXX'}
              </p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Mail className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
            <div>
              <p className="font-medium text-gray-900">Email</p>
              <p className="text-gray-600">info@fooddelivery.com</p>
            </div>
          </div>

          <div className="flex items-start gap-3">
            <Clock className="w-6 h-6 text-red-600 flex-shrink-0 mt-1" />
            <div>
              <p className="font-medium text-gray-900">Години роботи</p>
              <p className="text-gray-600">
                {restaurantInfo?.opening_hours || 'Пн-Нд: 09:00 - 22:00'}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Reviews Section */}
      <div className="bg-white rounded-xl shadow-md p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">Відгуки клієнтів</h2>
          {reviews.length > 0 && (
            <div className="flex items-center gap-2">
              <Star className="w-6 h-6 fill-yellow-400 text-yellow-400" />
              <span className="text-2xl font-bold text-gray-900">
                {calculateAverageRating()}
              </span>
              <span className="text-gray-500">({reviews.length} відгуків)</span>
            </div>
          )}
        </div>

        {reviews.length === 0 ? (
          <div className="text-center py-12">
            <Star className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500 text-lg">Поки що немає відгуків</p>
            <p className="text-gray-400 text-sm mt-2">
              Станьте першим, хто залишить відгук після замовлення!
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {reviews.map((review) => (
              <div
                key={review.id}
                className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
              >
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    {renderStars(review.rating)}
                    <span className="text-sm text-gray-500">
                      {new Date(review.created_at).toLocaleDateString('uk-UA', {
                        year: 'numeric',
                        month: 'long',
                        day: 'numeric'
                      })}
                    </span>
                  </div>
                </div>
                <p className="text-gray-700 leading-relaxed">{review.text}</p>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

