import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import type { Order } from '../types';
import { Package, Clock, CheckCircle, Truck, ArrowUpDown } from 'lucide-react';

const statusIcons: Record<string, any> = {
  pending: Clock,
  delivering: Truck,
  delivered: CheckCircle,
};

const statusLabels: Record<string, string> = {
  pending: 'Очікує',
  delivering: 'Доставляється',
  delivered: 'Доставлено',
};

type SortOption = 'price_desc' | 'price_asc' | 'status';

export default function Orders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<SortOption>('price_desc');
  const navigate = useNavigate();

  useEffect(() => {
    if (!localStorage.getItem('client_token')) {
      navigate('/');
      return;
    }
    fetchOrders();
  }, [navigate]);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/orders');
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  // Фільтрація та сортування замовлень
  const getFilteredAndSortedOrders = () => {
    let filtered = statusFilter === 'all' 
      ? [...orders] 
      : orders.filter((o) => o.status === statusFilter);

    // Сортування
    filtered.sort((a, b) => {
      switch (sortBy) {
        case 'price_desc':
          return b.total_price - a.total_price;
        case 'price_asc':
          return a.total_price - b.total_price;
        case 'status':
          const statusOrder = { pending: 0, delivering: 1, delivered: 2 };
          return (statusOrder[a.status as keyof typeof statusOrder] || 99) - 
                 (statusOrder[b.status as keyof typeof statusOrder] || 99);
        default:
          return 0;
      }
    });

    return filtered;
  };

  const filteredOrders = getFilteredAndSortedOrders();

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <div className="flex justify-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900"></div>
        </div>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <div className="text-center py-16 bg-white rounded-xl border border-neutral-200">
          <Package className="w-16 h-16 text-neutral-300 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-neutral-900 mb-2">У вас ще немає замовлень</h2>
          <p className="text-neutral-600 mb-6">Перегляньте наш каталог одягу!</p>
          <a
            href="/"
            className="inline-block bg-neutral-900 text-white px-6 py-3 rounded-lg font-medium hover:bg-black transition-colors"
          >
            Переглянути меню
          </a>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-4 md:p-8">
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl md:text-3xl font-bold text-neutral-900">Мої замовлення</h1>
        
        {/* Сортування */}
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-4 h-4 text-neutral-500" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className="px-3 py-2 border border-neutral-300 rounded-lg bg-white text-sm focus:ring-2 focus:ring-neutral-900 focus:border-transparent"
          >
            <option value="price_desc">Від дорожчих</option>
            <option value="price_asc">Від дешевших</option>
            <option value="status">За статусом</option>
          </select>
        </div>
      </div>

      {/* Фільтри статусів */}
      <div className="mb-6 flex items-center gap-2 overflow-x-auto pb-2">
        {[
          { value: 'all', label: 'Всі', icon: null },
          { value: 'pending', label: 'Очікує', icon: Clock },
          { value: 'delivering', label: 'Доставляється', icon: Truck },
          { value: 'delivered', label: 'Доставлено', icon: CheckCircle },
        ].map((filter) => {
          const FilterIcon = filter.icon;
          return (
            <button
              key={filter.value}
              onClick={() => setStatusFilter(filter.value)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all whitespace-nowrap ${
                statusFilter === filter.value
                  ? 'bg-neutral-900 text-white'
                  : 'bg-white text-neutral-700 border border-neutral-200 hover:border-neutral-300'
              }`}
            >
              {FilterIcon && <FilterIcon className="w-4 h-4" />}
              <span>{filter.label}</span>
              {filter.value === 'all' && (
                <span className={`ml-1 px-2 py-0.5 rounded-full text-xs font-semibold ${
                  statusFilter === 'all' ? 'bg-white/20 text-white' : 'bg-neutral-100 text-neutral-700'
                }`}>
                  {orders.length}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Grid з 3 колонками */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {filteredOrders.map((order) => {
          const StatusIcon = statusIcons[order.status] || Clock;
          const statusColor = order.status === 'delivered' 
            ? 'bg-green-50 text-green-700 border-green-200' 
            : order.status === 'delivering'
            ? 'bg-blue-50 text-blue-700 border-blue-200'
            : 'bg-yellow-50 text-yellow-700 border-yellow-200';
          
          return (
            <div key={order.id} className="bg-white rounded-xl border border-neutral-200 p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-neutral-900">
                      Замовлення #{order.id}
                    </h3>
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${statusColor}`}>
                      <StatusIcon className="w-3.5 h-3.5" />
                      {statusLabels[order.status] || order.status}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-500 mb-3">
                    {new Date(order.created_at).toLocaleString('uk-UA', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                  <p className="text-sm text-neutral-600 mb-1 line-clamp-2">
                    {order.delivery_address}
                  </p>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-neutral-100">
                <span className="text-xl font-bold text-neutral-900">
                  ₴{(order.total_price / 100).toFixed(2)}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
