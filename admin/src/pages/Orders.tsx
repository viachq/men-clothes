import { useEffect, useState } from 'react';
import api from '../api/client';
import type { Order, OrderDetails } from '../types';
import { Eye, Package, Clock, CheckCircle, XCircle, Truck } from 'lucide-react';

const statusColors: Record<string, string> = {
  pending: 'bg-yellow-100 text-yellow-800',
  accepted: 'bg-blue-100 text-blue-800',
  preparing: 'bg-purple-100 text-purple-800',
  ready: 'bg-green-100 text-green-800',
  delivering: 'bg-indigo-100 text-indigo-800',
  delivered: 'bg-green-100 text-green-800',
  cancelled: 'bg-red-100 text-red-800',
};

const statusIcons: Record<string, any> = {
  pending: Clock,
  accepted: CheckCircle,
  preparing: Package,
  ready: CheckCircle,
  delivering: Truck,
  delivered: CheckCircle,
  cancelled: XCircle,
};

export default function Orders() {
  const [orders, setOrders] = useState<Order[]>([]);
  const [selectedOrder, setSelectedOrder] = useState<OrderDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [modalOpen, setModalOpen] = useState(false);
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  useEffect(() => {
    fetchOrders();
  }, []);

  const fetchOrders = async () => {
    try {
      const response = await api.get('/admin/orders');
      setOrders(response.data);
    } catch (error) {
      console.error('Failed to fetch orders:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredOrders = statusFilter
    ? orders.filter((order) => order.status === statusFilter)
    : orders;

  const statusCounts = {
    all: orders.length,
    pending: orders.filter((o) => o.status === 'pending').length,
    preparing: orders.filter((o) => o.status === 'preparing').length,
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

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-white mb-8">Orders Management</h1>
        <div className="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 p-12">
          <div className="flex flex-col items-center justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-neutral-900 dark:border-white mb-4"></div>
            <p className="text-neutral-500 dark:text-neutral-400 font-medium">Loading orders...</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto">
      <div className="flex items-center justify-between mb-8">
        <h1 className="text-3xl font-bold text-neutral-900 dark:text-white">Orders Management</h1>

      </div>

      {/* Status Filters */}
      <div className="flex gap-3 mb-6 overflow-x-auto pb-2">
        <button
          onClick={() => setStatusFilter(null)}
          className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
            statusFilter === null
              ? 'bg-neutral-900 dark:bg-white text-white dark:text-black shadow-md'
              : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border border-neutral-300 dark:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-700'
          }`}
        >
          All Orders
          <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-opacity-20 bg-white">
            {statusCounts.all}
          </span>
        </button>
        <button
          onClick={() => setStatusFilter('pending')}
          className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
            statusFilter === 'pending'
              ? 'bg-yellow-500 text-white shadow-md'
              : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border border-neutral-300 dark:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-700'
          }`}
        >
          <Clock className="w-4 h-4 inline mr-1" />
          Pending
          <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-opacity-20 bg-white">
            {statusCounts.pending}
          </span>
        </button>
        <button
          onClick={() => setStatusFilter('preparing')}
          className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
            statusFilter === 'preparing'
              ? 'bg-purple-500 text-white shadow-md'
              : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border border-neutral-300 dark:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-700'
          }`}
        >
          <Package className="w-4 h-4 inline mr-1" />
          Preparing
          <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-opacity-20 bg-white">
            {statusCounts.preparing}
          </span>
        </button>
        <button
          onClick={() => setStatusFilter('delivering')}
          className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
            statusFilter === 'delivering'
              ? 'bg-indigo-500 text-white shadow-md'
              : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border border-neutral-300 dark:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-700'
          }`}
        >
          <Truck className="w-4 h-4 inline mr-1" />
          Delivering
          <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-opacity-20 bg-white">
            {statusCounts.delivering}
          </span>
        </button>
        <button
          onClick={() => setStatusFilter('delivered')}
          className={`px-4 py-2 rounded-lg font-medium transition-all whitespace-nowrap ${
            statusFilter === 'delivered'
              ? 'bg-green-500 text-white shadow-md'
              : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border border-neutral-300 dark:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-700'
          }`}
        >
          <CheckCircle className="w-4 h-4 inline mr-1" />
          Delivered
          <span className="ml-2 px-2 py-0.5 rounded-full text-xs bg-opacity-20 bg-white">
            {statusCounts.delivered}
          </span>
        </button>
      </div>

      {/* Table View */}
      <div className="bg-white dark:bg-neutral-900 rounded-xl shadow-sm border border-neutral-200 dark:border-neutral-700 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-neutral-200 dark:divide-neutral-700">
            <thead className="bg-neutral-50 dark:bg-neutral-800">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                  Order ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                  Customer
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                  Total
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                  Date
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white dark:bg-neutral-900 divide-y divide-neutral-200 dark:divide-neutral-700">
              {filteredOrders.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-12 text-center">
                    <div className="flex flex-col items-center justify-center">
                      <Package className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mb-4" />
                      <p className="text-neutral-500 dark:text-neutral-400 text-lg font-medium">No orders found</p>
                      <p className="text-neutral-400 dark:text-neutral-500 text-sm mt-2">
                        {statusFilter
                          ? 'Try selecting a different status filter'
                          : 'Orders will appear here once customers place them'}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filteredOrders.map((order) => {
                  const StatusIcon = statusIcons[order.status] || Clock;
                  return (
                    <tr key={order.id} className="hover:bg-neutral-50 dark:hover:bg-neutral-800">
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-neutral-900 dark:text-white">
                      #{order.id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500 dark:text-neutral-400">
                      User #{order.user_id}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-900 dark:text-white font-medium">
                      ₴{(order.total_price / 100).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-xs font-medium ${statusColors[order.status]}`}>
                        <StatusIcon className="w-3 h-3" />
                        {order.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-neutral-500 dark:text-neutral-400">
                      {new Date(order.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <button
                        onClick={() => fetchOrderDetails(order.id)}
                        className="inline-flex items-center gap-1 text-neutral-900 dark:text-white hover:text-neutral-700 dark:hover:text-neutral-300 font-medium"
                      >
                        <Eye className="w-4 h-4" />
                        View
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
            <div className="fixed inset-0 bg-neutral-900/50 dark:bg-black/70" onClick={() => setModalOpen(false)} />
            <div className="relative bg-white dark:bg-neutral-900 rounded-xl shadow-xl max-w-2xl w-full p-6 border dark:border-neutral-700">
              <h2 className="text-2xl font-bold text-neutral-900 dark:text-white mb-4">Order #{selectedOrder.id}</h2>

              <div className="space-y-4 mb-6">
                {/* Customer info */}
                {(selectedOrder.name || selectedOrder.surname || selectedOrder.phone || selectedOrder.email) && (
                  <div>
                    <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400 mb-1">Customer</h3>
                    {(selectedOrder.name || selectedOrder.surname) && (
                      <p className="text-neutral-900 dark:text-white font-medium">{[selectedOrder.name, selectedOrder.surname].filter(Boolean).join(' ')}</p>
                    )}
                    {selectedOrder.phone && <p className="text-neutral-700 dark:text-neutral-300 text-sm">{selectedOrder.phone}</p>}
                    {selectedOrder.email && <p className="text-neutral-700 dark:text-neutral-300 text-sm">{selectedOrder.email}</p>}
                  </div>
                )}

                <div>
                  <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400">Delivery Address</h3>
                  <p className="text-neutral-900 dark:text-white">{selectedOrder.delivery_address}</p>
                  {selectedOrder.delivery_method && (
                    <p className="text-neutral-500 dark:text-neutral-400 text-sm mt-1">
                      {selectedOrder.delivery_method === 'nova_poshta' ? 'Нова Пошта' : selectedOrder.delivery_method === 'ukrposhta' ? 'Укрпошта' : 'Самовивіз'}
                    </p>
                  )}
                </div>

                {selectedOrder.comment && (
                  <div>
                    <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400">Comment</h3>
                    <p className="text-neutral-700 dark:text-neutral-300 text-sm italic">{selectedOrder.comment}</p>
                  </div>
                )}

                {selectedOrder.delivery_time && (
                  <div>
                    <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400">Delivery Time</h3>
                    <p className="text-neutral-900 dark:text-white">{new Date(selectedOrder.delivery_time).toLocaleString()}</p>
                  </div>
                )}

                <div>
                  <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400 mb-2">Change Status</h3>
                  <select
                    value={selectedOrder.status}
                    onChange={(e) => updateOrderStatus(selectedOrder.id, e.target.value)}
                    className="w-full px-4 py-2 border border-neutral-300 dark:border-neutral-600 rounded-lg focus:ring-2 focus:ring-neutral-900 dark:focus:ring-white bg-white dark:bg-neutral-800 text-neutral-900 dark:text-white"
                  >
                    <option value="pending">Pending</option>
                    <option value="delivering">Delivering</option>
                    <option value="delivered">Delivered</option>
                    <option value="cancelled">Cancelled</option>
                  </select>
                </div>

                <div>
                  <h3 className="text-sm font-medium text-neutral-500 dark:text-neutral-400 mb-2">Order Items</h3>
                  <div className="border border-neutral-200 dark:border-neutral-700 rounded-lg overflow-hidden">
                    {selectedOrder.items.map((item) => (
                      <div key={item.id} className="flex justify-between items-center p-3 border-b border-neutral-200 dark:border-neutral-700 last:border-b-0">
                        <div>
                          <p className="font-medium text-neutral-900 dark:text-white">{item.menu_item_name}</p>
                          <p className="text-sm text-neutral-500 dark:text-neutral-400">Quantity: {item.quantity} × ₴{(item.price / 100).toFixed(2)}</p>
                        </div>
                        <p className="font-medium text-neutral-900 dark:text-white">₴{(item.subtotal / 100).toFixed(2)}</p>
                      </div>
                    ))}
                    <div className="flex justify-between items-center p-3 bg-neutral-50 dark:bg-neutral-800 font-bold text-neutral-900 dark:text-white">
                      <span>Total</span>
                      <span>₴{(selectedOrder.total_price / 100).toFixed(2)}</span>
                    </div>
                  </div>
                </div>
              </div>

              <button
                onClick={() => setModalOpen(false)}
                className="w-full bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 py-2 px-4 rounded-lg font-medium hover:bg-neutral-200 dark:hover:bg-neutral-700 transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
