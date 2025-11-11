import { useEffect, useState } from 'react';
import api from '../api/client';
import type { Stats } from '../types';
import { DollarSign, ShoppingBag, Star, Clock, Receipt } from 'lucide-react';

export default function Dashboard() {
  const [stats, setStats] = useState<Stats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const response = await api.get('/admin/stats/overview');
      setStats(response.data);
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-red-600"></div>
      </div>
    );
  }

  const cards = [
    {
      title: 'Total Orders',
      value: stats?.orders || 0,
      icon: ShoppingBag,
      color: 'bg-blue-500',
    },
    {
      title: 'Revenue',
      value: `₴${((stats?.revenue || 0) / 100).toFixed(2)}`,
      icon: DollarSign,
      color: 'bg-green-500',
    },
    {
      title: 'Average Order',
      value: `₴${((stats?.average_order || 0) / 100).toFixed(0)}`,
      icon: Receipt,
      color: 'bg-purple-500',
    },
    {
      title: 'Active Orders',
      value: stats?.active_orders || 0,
      icon: Clock,
      color: 'bg-orange-500',
    },
    {
      title: 'Menu Items',
      value: stats?.menu_items_count || 0,
      icon: Star,
      color: 'bg-yellow-500',
    },
  ];

  return (
    <div className="max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        {cards.map((card) => {
          const Icon = card.icon;
          return (
            <div key={card.title} className="bg-white rounded-xl shadow-sm p-6 border border-gray-100 hover:shadow-md transition-shadow">
              <div className="flex items-center justify-between mb-4">
                <div className={`${card.color} p-3 rounded-lg`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
              </div>
              <h3 className="text-gray-600 text-sm font-medium mb-1">{card.title}</h3>
              <p className="text-3xl font-bold text-gray-900">{card.value}</p>
            </div>
          );
        })}
      </div>

      {/* Top Items */}
      <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-100">
        <h2 className="text-xl font-bold text-gray-900 mb-4">Top Menu Items (Most Ordered)</h2>
        {stats?.top_items && stats.top_items.length > 0 ? (
          <div className="space-y-3">
            {stats.top_items.map((item, index) => (
              <div
                key={item.id}
                className="flex items-center gap-4 p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
              >
                <div className="flex items-center justify-center w-10 h-10 bg-gradient-to-br from-red-500 to-orange-500 text-white rounded-full font-bold text-lg shadow-md">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <h3 className="font-semibold text-gray-900 text-lg">{item.name}</h3>
                  <p className="text-sm text-gray-600 mt-1">
                    <span className="font-medium">{item.orders}</span> {item.orders === 1 ? 'замовлення' : 'замовлень'} • 
                    <span className="font-medium ml-1">{item.sold}</span> {item.sold === 1 ? 'продано' : 'продано'}
                  </p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No orders yet</p>
        )}
      </div>
    </div>
  );
}

