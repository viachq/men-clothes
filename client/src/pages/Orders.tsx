import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/client';
import type { Order } from '../types';
import { Package, Clock, CheckCircle, Truck, ArrowUpDown, XCircle } from 'lucide-react';
import { showSuccess, showError } from '../utils/notifications';

const statusIcons: Record<string, any> = {
  pending: Clock,
  delivering: Truck,
  delivered: CheckCircle,
  cancelled: XCircle,
};

const statusLabels: Record<string, string> = {
  pending: 'Очікує',
  delivering: 'Доставляється',
  delivered: 'Доставлено',
  cancelled: 'Скасовано',
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

  const cancelOrder = async (orderId: number) => {
    try {
      await api.put(`/orders/${orderId}/cancel`);
      showSuccess('Замовлення скасовано');
      fetchOrders();
    } catch (err: any) {
      showError(err.response?.data?.detail || 'Не вдалося скасувати замовлення');
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
          const statusOrder = { pending: 0, delivering: 1, delivered: 2, cancelled: 3 };
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
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900 dark:border-neutral-100"></div>
        </div>
      </div>
    );
  }

  if (orders.length === 0) {
    return (
      <div className="max-w-6xl mx-auto p-8">
        <div className="text-center py-16 bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700">
          <Package className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-neutral-900 dark:text-white mb-2">У вас ще немає замовлень</h2>
          <p className="text-neutral-600 dark:text-neutral-400 mb-6">Перегляньте наш каталог одягу!</p>
          <a
            href="/"
            className="inline-block bg-neutral-900 dark:bg-white text-white dark:text-black px-6 py-3 rounded-lg font-medium hover:bg-black dark:hover:bg-neutral-200 transition-colors"
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
        <h1 className="text-2xl md:text-3xl font-bold text-neutral-900 dark:text-white">Мої замовлення</h1>

        {/* Сортування */}
        <div className="flex items-center gap-2">
          <ArrowUpDown className="w-4 h-4 text-neutral-500 dark:text-neutral-400" />
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as SortOption)}
            className="px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg bg-white dark:bg-neutral-800 dark:text-white text-sm focus:ring-2 focus:ring-neutral-900 dark:focus:ring-neutral-100 focus:border-transparent"
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
          { value: 'cancelled', label: 'Скасовано', icon: XCircle },
        ].map((filter) => {
          const FilterIcon = filter.icon;
          return (
            <button
              key={filter.value}
              onClick={() => setStatusFilter(filter.value)}
              className={`flex items-center gap-2 px-4 py-2 rounded-lg font-medium text-sm transition-all whitespace-nowrap ${
                statusFilter === filter.value
                  ? 'bg-neutral-900 dark:bg-white text-white dark:text-black'
                  : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600'
              }`}
            >
              {FilterIcon && <FilterIcon className="w-4 h-4" />}
              <span>{filter.label}</span>
              {filter.value === 'all' && (
                <span className={`ml-1 px-2 py-0.5 rounded-full text-xs font-semibold ${
                  statusFilter === 'all' ? 'bg-white/20 text-white dark:bg-black/20 dark:text-black' : 'bg-neutral-100 dark:bg-neutral-700 text-neutral-700 dark:text-neutral-300'
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
            ? 'bg-green-50 text-green-700 border-green-200 dark:bg-green-900/30 dark:text-green-400 dark:border-green-800'
            : order.status === 'delivering'
            ? 'bg-blue-50 text-blue-700 border-blue-200 dark:bg-blue-900/30 dark:text-blue-400 dark:border-blue-800'
            : order.status === 'cancelled'
            ? 'bg-red-50 text-red-700 border-red-200 dark:bg-red-900/30 dark:text-red-400 dark:border-red-800'
            : 'bg-yellow-50 text-yellow-700 border-yellow-200 dark:bg-yellow-900/30 dark:text-yellow-400 dark:border-yellow-800';

          return (
            <div key={order.id} className="bg-white dark:bg-neutral-900 rounded-xl border border-neutral-200 dark:border-neutral-700 p-5 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-4">
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-lg font-semibold text-neutral-900 dark:text-white">
                      Замовлення #{order.id}
                    </h3>
                    <span className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-medium border ${statusColor}`}>
                      <StatusIcon className="w-3.5 h-3.5" />
                      {statusLabels[order.status] || order.status}
                    </span>
                  </div>
                  <p className="text-xs text-neutral-500 dark:text-neutral-400 mb-3">
                    {new Date(order.created_at).toLocaleString('uk-UA', {
                      day: '2-digit',
                      month: '2-digit',
                      year: 'numeric',
                      hour: '2-digit',
                      minute: '2-digit'
                    })}
                  </p>
                  <div className="space-y-1 text-sm text-neutral-600 dark:text-neutral-400">
                    {(order.name || order.surname) && (
                      <p className="font-medium text-neutral-800 dark:text-neutral-200">
                        {[order.name, order.surname].filter(Boolean).join(' ')}
                      </p>
                    )}
                    {order.phone && <p>{order.phone}</p>}
                    <p className="line-clamp-2">{order.delivery_address}</p>
                    {order.delivery_method && (
                      <p className="text-xs text-neutral-500 dark:text-neutral-500">
                        {order.delivery_method === 'nova_poshta' ? 'Нова Пошта' : order.delivery_method === 'ukrposhta' ? 'Укрпошта' : 'Самовивіз'}
                      </p>
                    )}
                    {order.comment && (
                      <p className="text-xs text-neutral-400 dark:text-neutral-500 italic line-clamp-1">{order.comment}</p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-neutral-100 dark:border-neutral-800">
                <div>
                  <span className="text-xl font-bold text-neutral-900 dark:text-white">
                    ₴{(order.total_price / 100).toFixed(2)}
                  </span>
                  {order.discount > 0 && (
                    <span className="ml-2 text-xs text-green-600 dark:text-green-400 font-medium">
                      (-₴{(order.discount / 100).toFixed(0)} промокод)
                    </span>
                  )}
                </div>
                {order.status === 'pending' && (
                  <button
                    onClick={() => cancelOrder(order.id)}
                    className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-semibold text-red-600 dark:text-red-400 border border-red-200 dark:border-red-800 rounded-lg hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Скасувати
                  </button>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
