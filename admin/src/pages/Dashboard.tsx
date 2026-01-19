import { useEffect, useState } from 'react';
import api from '../api/client';
import type { Order, OrderDetails, User } from '../types';
import { Clock, Eye, Package, Truck, CheckCircle, UserCircle, Shield, ShoppingBag } from 'lucide-react';
import OrdersChart from '../components/OrdersChart';

interface OrdersData {
  date: string;
  orders: number;
}

interface ProductsData {
  date: string;
  total_quantity: number;
  unique_products: number;
  top_products: Array<{ id: number; name: string; quantity: number }>;
}

type DashboardTab = 'overview' | 'orders' | 'users';

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  delivering: 'bg-indigo-100 text-indigo-800',
  delivered: 'bg-green-100 text-green-800',
};

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

const roleIcons = {
  client: ShoppingBag,
  manager: Shield,
  system_admin: Shield,
};

const roleColors = {
  client: 'bg-blue-100 text-blue-800',
  manager: 'bg-green-100 text-green-800',
  system_admin: 'bg-red-100 text-red-800',
};

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<DashboardTab>('overview');
  
  // Overview state
  const [ordersData, setOrdersData] = useState<OrdersData[]>([]);
  const [productsData, setProductsData] = useState<ProductsData[]>([]);
  const [loading, setLoading] = useState(false);
  
  // Orders state
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<OrderDetails | null>(null);
  const [ordersLoading, setOrdersLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);
  
  // Users state
  const [users, setUsers] = useState<User[]>([]);
  const [usersLoading, setUsersLoading] = useState(true);

  useEffect(() => {
    fetchOrdersData();
    fetchProductsData();
    fetchOrders();
    fetchUsers();
  }, []);


  const fetchOrdersData = async () => {
    try {
      const response = await api.get('/admin/stats/orders-by-day?period=month');
      setOrdersData(response.data);
    } catch (error: any) {
      console.error('Failed to fetch orders data:', error);
    }
  };

  const fetchProductsData = async () => {
    try {
      const response = await api.get('/admin/stats/products-by-period?period=month');
      setProductsData(response.data);
    } catch (error: any) {
      console.error('Failed to fetch products data:', error);
    }
  };

  const fetchOrders = async () => {
    try {
      const response = await api.get('/admin/orders');
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setOrdersLoading(false);
    }
  };

  const fetchUsers = async () => {
    try {
      const response = await api.get('/admin/users/');
      setUsers(response.data);
    } finally {
      setUsersLoading(false);
    }
  };

  const filteredOrders = statusFilter
    ? orders.filter((order) => order.status === statusFilter)
    : orders;

  const statusCounts = {
    all: orders.length,
    pending: orders.filter((o) => o.status === 'pending').length,
    delivering: orders.filter((o) => o.status === 'delivering').length,
    delivered: orders.filter((o) => o.status === 'delivered').length,
  };

  const fetchOrderDetails = async (orderId: number) => {
    try {
      const response = await api.get(`/admin/orders/${orderId}`);
      setSelectedOrder(response.data);
      setModalOpen(true);
    } catch (error) {
      console.error('Failed to fetch order details:', error);
    }
  };

  const updateOrderStatus = async (orderId: number, newStatus: string) => {
    try {
      await api.put(`/admin/orders/${orderId}/status`, null, {
        params: { status: newStatus },
      });
      fetchOrders();
      if (selectedOrder?.id === orderId) {
        fetchOrderDetails(orderId);
      }
    } catch (error) {
      console.error('Failed to update status:', error);
    }
  };

  const updateRole = async (userId: number, newRole: string) => {
    try {
      await api.put(`/admin/users/${userId}/role`, null, { params: { role: newRole } });
      fetchUsers();
    } catch (error) {
      console.error('Failed to update role:', error);
    }
  };

  const currentUserRole = localStorage.getItem('user_role') || '';
  const canEditRoles = currentUserRole === 'system_admin';

  return (
    <div className="max-w-[1600px] mx-auto space-y-8">
      {/* Tabs */}
      <div className="flex items-center justify-between border-b-2 border-neutral-200 pb-2">
        <div className="flex gap-1">
          <button
            onClick={() => setActiveTab('overview')}
            className={`px-6 py-3 font-semibold transition-colors relative ${
              activeTab === 'overview'
                ? 'text-neutral-900'
                : 'text-neutral-500 hover:text-neutral-700'
            }`}
          >
            Огляд
            {activeTab === 'overview' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-neutral-900"></div>
            )}
          </button>
          <button
            onClick={() => setActiveTab('orders')}
            className={`px-6 py-3 font-semibold transition-colors relative ${
              activeTab === 'orders'
                ? 'text-neutral-900'
                : 'text-neutral-500 hover:text-neutral-700'
            }`}
          >
            Замовлення
            {activeTab === 'orders' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-neutral-900"></div>
            )}
          </button>
          <button
            onClick={() => setActiveTab('users')}
            className={`px-6 py-3 font-semibold transition-colors relative ${
              activeTab === 'users'
                ? 'text-neutral-900'
                : 'text-neutral-500 hover:text-neutral-700'
            }`}
          >
            Користувачі
            {activeTab === 'users' && (
              <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-neutral-900"></div>
            )}
          </button>
              </div>
      </div>

      {/* Overview Tab */}
      {activeTab === 'overview' && (
        <>
      {/* Charts Section */}
          <div className="grid grid-cols-1 gap-6">
            <div className="bg-white rounded-2xl p-8 border-2 border-neutral-200 shadow-sm">
              <div className="mb-6">
                <h2 className="text-2xl font-black text-neutral-900 tracking-tight mb-2">
                  Замовлення за місяць
                </h2>
                <p className="text-neutral-500 text-sm">
                  Динаміка замовлень за останній місяць
                </p>
          </div>
          <OrdersChart data={ordersData} />
              {productsData.length > 0 && (
                <div className="mt-8 pt-8 border-t border-neutral-200">
                  <h3 className="text-lg font-bold text-neutral-900 mb-6 uppercase tracking-wider">Детальна інформація по товарах</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {productsData.map((dayData, idx) => (
                      <div key={idx} className="bg-neutral-50 rounded-lg p-5 border-2 border-neutral-200 hover:border-neutral-300 hover:shadow-md transition-all">
                        <div className="flex items-center justify-between mb-4 pb-3 border-b border-neutral-200">
                          <span className="font-bold text-lg text-neutral-900">{dayData.date}</span>
                          <span className="text-sm text-neutral-600 font-medium">
                            {dayData.unique_products} товарів • {dayData.total_quantity} шт. продано
                          </span>
                        </div>
                        {dayData.top_products.length > 0 && (
                          <div className="space-y-3">
                            {dayData.top_products.slice(0, 5).map((product) => (
                              <div key={product.id} className="flex items-center justify-between text-sm">
                                <span className="text-neutral-700 truncate flex-1 font-medium">{product.name}</span>
                                <span className="text-neutral-900 font-bold ml-3">{product.quantity} шт.</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
        </div>
      </div>
        </>
      )}

      {/* Orders Tab */}
      {activeTab === 'orders' && (
        <>
          {ordersLoading ? (
            <div className="flex justify-center p-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900"></div>
        </div>
          ) : (
            <>
              <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
                  <button
                    onClick={() => setStatusFilter(null)}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all whitespace-nowrap ${
                      statusFilter === null
                        ? 'bg-neutral-900 text-white shadow-lg'
                        : 'bg-white text-neutral-700 border-2 border-neutral-200 hover:border-neutral-300 hover:bg-neutral-50'
                    }`}
                  >
                    <span>Всі</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                      statusFilter === null ? 'bg-white/20 text-white' : 'bg-neutral-100 text-neutral-700'
                    }`}>
                      {statusCounts.all}
                    </span>
                  </button>
                  <button
                    onClick={() => setStatusFilter('pending')}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all whitespace-nowrap ${
                      statusFilter === 'pending'
                        ? 'bg-yellow-500 text-white shadow-lg'
                        : 'bg-white text-neutral-700 border-2 border-neutral-200 hover:border-yellow-300 hover:bg-yellow-50'
                    }`}
                  >
                    <Clock className="w-4 h-4" />
                    <span>Очікує</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                      statusFilter === 'pending' ? 'bg-white/20 text-white' : 'bg-neutral-100 text-neutral-700'
                    }`}>
                      {statusCounts.pending}
                    </span>
                  </button>
                  <button
                    onClick={() => setStatusFilter('delivering')}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all whitespace-nowrap ${
                      statusFilter === 'delivering'
                        ? 'bg-indigo-500 text-white shadow-lg'
                        : 'bg-white text-neutral-700 border-2 border-neutral-200 hover:border-indigo-300 hover:bg-indigo-50'
                    }`}
                  >
                    <Truck className="w-4 h-4" />
                    <span>Доставляється</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                      statusFilter === 'delivering' ? 'bg-white/20 text-white' : 'bg-neutral-100 text-neutral-700'
                    }`}>
                      {statusCounts.delivering}
                    </span>
                  </button>
                  <button
                    onClick={() => setStatusFilter('delivered')}
                    className={`flex items-center gap-2 px-4 py-2.5 rounded-lg font-semibold text-sm transition-all whitespace-nowrap ${
                      statusFilter === 'delivered'
                        ? 'bg-green-500 text-white shadow-lg'
                        : 'bg-white text-neutral-700 border-2 border-neutral-200 hover:border-green-300 hover:bg-green-50'
                    }`}
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>Доставлено</span>
                    <span className={`px-2 py-0.5 rounded-full text-xs font-bold ${
                      statusFilter === 'delivered' ? 'bg-white/20 text-white' : 'bg-neutral-100 text-neutral-700'
                    }`}>
                      {statusCounts.delivered}
                    </span>
                  </button>
                </div>

              <div className="bg-white rounded-2xl border-2 border-neutral-200 shadow-sm overflow-hidden">
                  <div className="overflow-x-auto">
                    <table className="min-w-full">
                      <thead>
                        <tr className="bg-neutral-50 border-b-2 border-neutral-200">
                          <th className="px-6 py-4 text-left">
                            <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">ID</span>
                          </th>
                          <th className="px-6 py-4 text-left">
                            <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Користувач</span>
                          </th>
                          <th className="px-6 py-4 text-left">
                            <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Сума</span>
                          </th>
                          <th className="px-6 py-4 text-left">
                            <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Статус</span>
                          </th>
                          <th className="px-6 py-4 text-left">
                            <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Дата</span>
                          </th>
                          <th className="px-6 py-4 text-left">
                            <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Дії</span>
                          </th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-neutral-100">
                        {filteredOrders.length === 0 ? (
                          <tr>
                            <td colSpan={6} className="px-6 py-16 text-center">
                              <div className="flex flex-col items-center justify-center">
                                <Package className="w-16 h-16 text-neutral-300 mb-4" />
                                <p className="text-neutral-500 text-lg font-semibold">Замовлень не знайдено</p>
                                <p className="text-neutral-400 text-sm mt-2">
                                  {statusFilter ? 'Спробуйте змінити фільтр статусу' : 'Замовлення з\'являться тут, коли клієнти їх розмістять'}
                                </p>
                              </div>
                            </td>
                          </tr>
                        ) : (
                          filteredOrders.map((order) => {
                            const StatusIcon = statusIcons[order.status] || Clock;
              return (
                              <tr key={order.id} className="hover:bg-neutral-50/50 transition-all duration-150 group">
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="text-sm font-bold text-neutral-900">#{order.id}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="text-sm font-medium text-neutral-600">User #{order.user_id}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="text-base font-black text-neutral-900">₴{(order.total_price / 100).toFixed(2)}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <div className="flex items-center gap-2">
                                    <div className={`w-0.5 h-6 rounded-full ${
                                      order.status === 'pending' ? 'bg-yellow-500' :
                                      order.status === 'delivering' ? 'bg-indigo-500' :
                                      'bg-green-500'
                                    }`}></div>
                                    <select
                                      value={order.status}
                                      onChange={(e) => updateOrderStatus(order.id, e.target.value)}
                                      className={`px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wide border-2 focus:outline-none focus:ring-2 focus:ring-offset-1 cursor-pointer transition-all ${
                                        order.status === 'pending' 
                                          ? 'bg-yellow-100 text-yellow-800 border-yellow-300 hover:border-yellow-400 focus:ring-yellow-500'
                                          : order.status === 'delivering'
                                          ? 'bg-indigo-100 text-indigo-800 border-indigo-300 hover:border-indigo-400 focus:ring-indigo-500'
                                          : 'bg-green-100 text-green-800 border-green-300 hover:border-green-400 focus:ring-green-500'
                                      }`}
                                    >
                                      <option value="pending">Очікує</option>
                                      <option value="delivering">Доставляється</option>
                                      <option value="delivered">Доставлено</option>
                                    </select>
                                  </div>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <span className="text-sm font-medium text-neutral-500">{new Date(order.created_at).toLocaleDateString('uk-UA')}</span>
                                </td>
                                <td className="px-6 py-4 whitespace-nowrap">
                                  <button
                                    onClick={() => fetchOrderDetails(order.id)}
                                    className="inline-flex items-center gap-2 px-3 py-1.5 text-sm font-semibold text-neutral-700 hover:text-neutral-900 hover:bg-neutral-100 rounded-lg transition-all duration-150"
                                  >
                                    <Eye className="w-4 h-4" />
                                    <span>Переглянути</span>
                                  </button>
                                </td>
                              </tr>
                            );
                          })
                        )}
                      </tbody>
                    </table>
                  </div>
                </div>

              {/* Order Details Modal */}
              {modalOpen && selectedOrder && (
                <div className="fixed inset-0 z-50 overflow-y-auto">
                  <div className="flex items-center justify-center min-h-screen px-4">
                    <div className="fixed inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setModalOpen(false)} />
                    <div className="relative bg-white rounded-3xl shadow-2xl max-w-2xl w-full overflow-hidden border-2 border-neutral-200">
                      <div className="relative bg-gradient-to-r from-neutral-900 via-neutral-800 to-neutral-900 px-8 py-6">
                        <div className="absolute top-0 left-0 right-0 h-1 bg-white/20"></div>
                        <h2 className="text-2xl font-black text-white tracking-tight uppercase">Замовлення #{selectedOrder.id}</h2>
                      </div>
                      <div className="p-8 space-y-6">
                        <div>
                          <h3 className="text-xs font-bold text-neutral-600 uppercase tracking-wider mb-2">Адреса доставки</h3>
                          <p className="text-neutral-900">{selectedOrder.delivery_address}</p>
                        </div>

                        <div>
                          <h3 className="text-xs font-bold text-neutral-600 uppercase tracking-wider mb-3">Товари</h3>
                          <div className="border-2 border-neutral-200 rounded-xl overflow-hidden">
                            {selectedOrder.items.map((item) => (
                              <div key={item.id} className="flex justify-between items-center p-4 border-b-2 last:border-b-0 border-neutral-100">
                                <div>
                                  <p className="font-semibold text-neutral-900">{item.menu_item_name}</p>
                                  <p className="text-sm text-neutral-500">Кількість: {item.quantity} × ₴{(item.price / 100).toFixed(2)}</p>
                                </div>
                                <p className="font-semibold text-neutral-900">₴{(item.subtotal / 100).toFixed(2)}</p>
                              </div>
                            ))}
                            <div className="flex justify-between items-center p-4 bg-neutral-50 font-bold">
                              <span>Всього</span>
                              <span className="text-neutral-900">₴{(selectedOrder.total_price / 100).toFixed(2)}</span>
                            </div>
                          </div>
                        </div>

                        <button
                          onClick={() => setModalOpen(false)}
                          className="w-full py-3.5 bg-neutral-100 text-neutral-700 rounded-xl font-semibold hover:bg-neutral-200 transition-colors"
                        >
                          Закрити
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </>
          )}
        </>
      )}

      {/* Users Tab */}
      {activeTab === 'users' && (
        <>
          {usersLoading ? (
            <div className="flex justify-center p-8">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900"></div>
            </div>
          ) : (
            <div className="bg-white rounded-2xl border-2 border-neutral-200 shadow-sm overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead>
                    <tr className="bg-neutral-50 border-b-2 border-neutral-200">
                      <th className="px-6 py-4 text-left">
                        <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Ім'я користувача</span>
                      </th>
                      <th className="px-6 py-4 text-left">
                        <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Роль</span>
                      </th>
                      <th className="px-6 py-4 text-center">
                        <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Замовлень</span>
                      </th>
                      <th className="px-6 py-4 text-left">
                        <span className="text-xs font-black text-neutral-700 uppercase tracking-widest">Дії</span>
                      </th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-neutral-100">
                    {users.map((user) => {
                      const RoleIcon = roleIcons[user.role as keyof typeof roleIcons];
                      const orderCount = orders.filter(order => order.user_id === user.id).length;
                      return (
                        <tr 
                          key={user.id} 
                          className="hover:bg-neutral-50/50 transition-all duration-150 group"
                        >
                          <td className="px-6 py-4">
                            <span className="text-base font-bold text-neutral-900">{user.username}</span>
                          </td>
                          <td className="px-6 py-4">
                            <div className="flex items-center gap-3">
                              <div className={`w-0.5 h-8 rounded-full ${
                                user.role === 'system_admin' ? 'bg-red-500' : 
                                user.role === 'manager' ? 'bg-green-500' : 
                                'bg-blue-500'
                              }`}></div>
                              <span className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wide ${roleColors[user.role as keyof typeof roleColors]}`}>
                                <RoleIcon className="w-3.5 h-3.5" />
                                {user.role === 'system_admin' ? 'System Admin' : user.role === 'manager' ? 'Manager' : 'Client'}
                              </span>
                            </div>
                          </td>
                          <td className="px-6 py-4 text-center">
                            <div className="inline-flex items-center gap-2 px-3 py-1.5 bg-neutral-100 rounded-lg group-hover:bg-neutral-200 transition-colors">
                              <Package className="w-4 h-4 text-neutral-600" />
                              <span className="text-lg font-black text-neutral-900">{orderCount}</span>
                              <span className="text-xs font-semibold text-neutral-500">шт.</span>
                            </div>
                          </td>
                          <td className="px-6 py-4">
                            {canEditRoles ? (
                              <select
                                value={user.role}
                                onChange={(e) => updateRole(user.id, e.target.value)}
                                className="px-3 py-2 border-2 border-neutral-300 rounded-lg text-sm font-semibold text-neutral-900 focus:outline-none focus:ring-2 focus:ring-neutral-900 focus:border-neutral-900 bg-white hover:border-neutral-400 hover:bg-neutral-50 transition-all cursor-pointer"
                              >
                                <option value="client">Client</option>
                                <option value="manager">Manager</option>
                                <option value="system_admin">System Admin</option>
                              </select>
                            ) : (
                              <span className="text-xs font-medium text-neutral-400 italic">Тільки перегляд</span>
                            )}
                          </td>
                        </tr>
              );
            })}
                  </tbody>
                </table>
          </div>
          </div>
        )}
        </>
      )}
    </div>
  );
}
