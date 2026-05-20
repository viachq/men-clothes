import { useEffect, useState } from 'react';
import api from '../api/client';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { BarChart3, ShoppingCart, TrendingUp, DollarSign, Package, Users } from 'lucide-react';

interface Summary {
  total_orders: number;
  total_revenue: number;
  avg_order_value: number;
  new_customers: number;
  new_customers_today: number;
  new_customers_week: number;
  orders_by_status: Array<{ status: string; count: number }>;
  top_products: Array<{ name: string; total_qty: number; total_revenue: number }>;
}

interface TopProduct {
  menu_item_id: number;
  name: string;
  total_qty: number;
  total_revenue: number;
}

interface RevenueByPeriod {
  period: string;
  revenue: number;
  orders: number;
}

type PeriodOption = 7 | 30 | 90;

const STATUS_COLORS: Record<string, string> = {
  pending: '#eab308',
  delivering: '#6366f1',
  delivered: '#22c55e',
  cancelled: '#ef4444',
};

const STATUS_LABELS: Record<string, string> = {
  pending: 'Очікує',
  delivering: 'Доставляється',
  delivered: 'Доставлено',
  cancelled: 'Скасовано',
};

const PIE_COLORS = ['#eab308', '#6366f1', '#22c55e', '#f43f5e', '#8b5cf6', '#06b6d4'];

export default function Analytics() {
  const [period, setPeriod] = useState<PeriodOption>(30);
  const [summary, setSummary] = useState<Summary | null>(null);
  const [topProducts, setTopProducts] = useState<TopProduct[]>([]);
  const [revenueData, setRevenueData] = useState<RevenueByPeriod[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAll();
  }, [period]);

  const fetchAll = async () => {
    setLoading(true);
    try {
      const [summaryRes, topRes, revenueRes] = await Promise.all([
        api.get(`/admin/analytics/summary?days=${period}`),
        api.get(`/admin/analytics/top-products?days=${period}&limit=10`),
        api.get(`/admin/analytics/revenue-by-period?days=${period}&group_by=day`),
      ]);
      setSummary(summaryRes.data);
      setTopProducts(topRes.data);
      setRevenueData(revenueRes.data);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setLoading(false);
    }
  };

  const formatUAH = (kopiyky: number) => {
    return `₴${(kopiyky / 100).toFixed(2)}`;
  };

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
          <BarChart3 className="w-6 h-6 text-neutral-900 dark:text-white" />
          <h1 className="text-2xl font-black text-neutral-900 dark:text-white tracking-tight uppercase">
            Аналітика
          </h1>
        </div>

        {/* Period selector */}
        <div className="flex gap-2">
          {([7, 30, 90] as PeriodOption[]).map((p) => (
            <button
              key={p}
              onClick={() => setPeriod(p)}
              className={`px-4 py-2.5 rounded-lg font-semibold text-sm transition-all ${
                period === p
                  ? 'bg-neutral-900 dark:bg-white text-white dark:text-black shadow-lg'
                  : 'bg-white dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300 border-2 border-neutral-200 dark:border-neutral-700 hover:border-neutral-300 dark:hover:border-neutral-600 hover:bg-neutral-50 dark:hover:bg-neutral-700'
              }`}
            >
              {p}д
            </button>
          ))}
        </div>
      </div>

      {/* Summary cards */}
      {summary && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          <div className="bg-white dark:bg-neutral-900 rounded-2xl p-6 border-2 border-neutral-200 dark:border-neutral-700 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-neutral-100 dark:bg-neutral-800 rounded-xl flex items-center justify-center">
                <ShoppingCart className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
              </div>
              <span className="text-xs font-bold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                Всього замовлень
              </span>
            </div>
            <p className="text-4xl font-black text-neutral-900 dark:text-white">{summary.total_orders}</p>
          </div>

          <div className="bg-white dark:bg-neutral-900 rounded-2xl p-6 border-2 border-neutral-200 dark:border-neutral-700 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-neutral-100 dark:bg-neutral-800 rounded-xl flex items-center justify-center">
                <DollarSign className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
              </div>
              <span className="text-xs font-bold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                Загальний дохід
              </span>
            </div>
            <p className="text-4xl font-black text-neutral-900 dark:text-white">
              {formatUAH(summary.total_revenue)}
            </p>
          </div>

          <div className="bg-white dark:bg-neutral-900 rounded-2xl p-6 border-2 border-neutral-200 dark:border-neutral-700 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-neutral-100 dark:bg-neutral-800 rounded-xl flex items-center justify-center">
                <TrendingUp className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
              </div>
              <span className="text-xs font-bold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                Середній чек
              </span>
            </div>
            <p className="text-4xl font-black text-neutral-900 dark:text-white">
              {formatUAH(summary.avg_order_value)}
            </p>
          </div>

          <div className="bg-white dark:bg-neutral-900 rounded-2xl p-6 border-2 border-neutral-200 dark:border-neutral-700 shadow-sm">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-neutral-100 dark:bg-neutral-800 rounded-xl flex items-center justify-center">
                <Users className="w-5 h-5 text-neutral-700 dark:text-neutral-300" />
              </div>
              <span className="text-xs font-bold text-neutral-500 dark:text-neutral-400 uppercase tracking-wider">
                Нові клієнти
              </span>
            </div>
            <p className="text-4xl font-black text-neutral-900 dark:text-white">{summary.new_customers}</p>
            <div className="flex gap-3 mt-2 text-xs text-neutral-500 dark:text-neutral-400">
              <span>Сьогодні: <b className="text-neutral-900 dark:text-white">{summary.new_customers_today}</b></span>
              <span>За тиждень: <b className="text-neutral-900 dark:text-white">{summary.new_customers_week}</b></span>
            </div>
          </div>
        </div>
      )}

      {/* Charts row */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue chart */}
        <div className="lg:col-span-2 bg-white dark:bg-neutral-900 rounded-2xl p-8 border-2 border-neutral-200 dark:border-neutral-700 shadow-sm">
          <div className="mb-6">
            <h2 className="text-2xl font-black text-neutral-900 dark:text-white tracking-tight mb-2">
              Дохід за період
            </h2>
            <p className="text-neutral-500 dark:text-neutral-400 text-sm">Динаміка доходу за останні {period} днів</p>
          </div>
          <div style={{ minHeight: 320, height: 320 }}>
            <ResponsiveContainer width="100%" height={320}>
              <AreaChart
                data={revenueData.map((d) => ({
                  ...d,
                  revenueUAH: d.revenue / 100,
                }))}
                margin={{ top: 15, right: 25, left: 5, bottom: 10 }}
              >
                <defs>
                  <linearGradient id="colorRevenueGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#171717" stopOpacity={0.25} />
                    <stop offset="50%" stopColor="#404040" stopOpacity={0.15} />
                    <stop offset="100%" stopColor="#171717" stopOpacity={0} />
                  </linearGradient>
                  <linearGradient id="colorRevenueLine" x1="0" y1="0" x2="1" y2="0">
                    <stop offset="0%" stopColor="#171717" />
                    <stop offset="100%" stopColor="#525252" />
                  </linearGradient>
                </defs>
                <CartesianGrid
                  strokeDasharray="2 4"
                  stroke="#e5e7eb"
                  vertical={false}
                  strokeWidth={1}
                />
                <XAxis
                  dataKey="period"
                  stroke="#9ca3af"
                  style={{ fontSize: '11px', fontWeight: '500' }}
                  tickLine={false}
                  axisLine={{ stroke: '#e5e7eb', strokeWidth: 1.5 }}
                />
                <YAxis
                  stroke="#9ca3af"
                  style={{ fontSize: '11px', fontWeight: '500' }}
                  tickLine={false}
                  axisLine={{ stroke: '#e5e7eb', strokeWidth: 1.5 }}
                  width={60}
                  tickFormatter={(v) => `₴${v}`}
                />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#ffffff',
                    border: '2px solid #171717',
                    borderRadius: '12px',
                    boxShadow: '0 8px 16px rgba(0, 0, 0, 0.12)',
                    padding: '10px 14px',
                  }}
                  labelStyle={{
                    fontWeight: '800',
                    color: '#171717',
                    fontSize: '12px',
                    textTransform: 'uppercase' as const,
                    letterSpacing: '0.5px',
                    marginBottom: '6px',
                  }}
                  formatter={(value: number) => [`₴${value.toFixed(2)}`, 'Дохід']}
                  cursor={{ stroke: '#171717', strokeWidth: 2, strokeDasharray: '3 3' }}
                />
                <Area
                  type="monotone"
                  dataKey="revenueUAH"
                  stroke="url(#colorRevenueLine)"
                  strokeWidth={2.5}
                  fillOpacity={1}
                  fill="url(#colorRevenueGradient)"
                  dot={{ fill: '#171717', strokeWidth: 2, r: 4 }}
                  activeDot={{ r: 6, stroke: '#171717', strokeWidth: 2, fill: '#ffffff' }}
                  isAnimationActive={false}
                />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Orders by status - pie chart */}
        <div className="bg-white dark:bg-neutral-900 rounded-2xl p-8 border-2 border-neutral-200 dark:border-neutral-700 shadow-sm">
          <div className="mb-6">
            <h2 className="text-lg font-black text-neutral-900 dark:text-white tracking-tight mb-2">
              Замовлення за статусом
            </h2>
          </div>
          {summary && summary.orders_by_status.length > 0 ? (
            <div style={{ minHeight: 280, height: 280 }}>
              <ResponsiveContainer width="100%" height={280}>
                <PieChart>
                  <Pie
                    data={summary.orders_by_status.map((s) => ({
                      name: STATUS_LABELS[s.status] || s.status,
                      value: s.count,
                      fill: STATUS_COLORS[s.status] || '#a3a3a3',
                    }))}
                    cx="50%"
                    cy="50%"
                    innerRadius={50}
                    outerRadius={90}
                    paddingAngle={4}
                    dataKey="value"
                  >
                    {summary.orders_by_status.map((s, index) => (
                      <Cell
                        key={`cell-${index}`}
                        fill={STATUS_COLORS[s.status] || PIE_COLORS[index % PIE_COLORS.length]}
                      />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{
                      backgroundColor: '#ffffff',
                      border: '2px solid #171717',
                      borderRadius: '12px',
                      boxShadow: '0 8px 16px rgba(0, 0, 0, 0.12)',
                      padding: '10px 14px',
                    }}
                  />
                  <Legend
                    verticalAlign="bottom"
                    height={36}
                    formatter={(value: string) => (
                      <span className="text-xs font-semibold text-neutral-700 dark:text-neutral-300">{value}</span>
                    )}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="flex items-center justify-center h-64">
              <p className="text-neutral-400 dark:text-neutral-500 text-sm">Немає даних</p>
            </div>
          )}
        </div>
      </div>

      {/* Top Products */}
      <div className="bg-white dark:bg-neutral-900 rounded-2xl border-2 border-neutral-200 dark:border-neutral-700 shadow-sm overflow-hidden">
        <div className="px-8 py-6 border-b-2 border-neutral-200 dark:border-neutral-700">
          <h2 className="text-2xl font-black text-neutral-900 dark:text-white tracking-tight mb-1">
            Топ товари
          </h2>
          <p className="text-neutral-500 dark:text-neutral-400 text-sm">
            Найпопулярніші товари за останні {period} днів
          </p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full">
            <thead>
              <tr className="bg-neutral-50 dark:bg-neutral-800 border-b-2 border-neutral-200 dark:border-neutral-700">
                <th className="px-6 py-4 text-center w-16">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">
                    #
                  </span>
                </th>
                <th className="px-6 py-4 text-left">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">
                    Товар
                  </span>
                </th>
                <th className="px-6 py-4 text-center">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">
                    Продано (шт.)
                  </span>
                </th>
                <th className="px-6 py-4 text-right">
                  <span className="text-xs font-black text-neutral-700 dark:text-neutral-300 uppercase tracking-widest">
                    Дохід
                  </span>
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-neutral-100 dark:divide-neutral-800">
              {topProducts.length === 0 ? (
                <tr>
                  <td colSpan={4} className="px-6 py-16 text-center">
                    <div className="flex flex-col items-center justify-center">
                      <Package className="w-16 h-16 text-neutral-300 dark:text-neutral-600 mb-4" />
                      <p className="text-neutral-500 dark:text-neutral-400 text-lg font-semibold">Немає даних</p>
                    </div>
                  </td>
                </tr>
              ) : (
                topProducts.map((product, idx) => (
                  <tr
                    key={product.menu_item_id}
                    className="hover:bg-neutral-50/50 dark:hover:bg-neutral-800/50 transition-all duration-150"
                  >
                    <td className="px-6 py-4 text-center">
                      <span
                        className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-black ${
                          idx === 0
                            ? 'bg-neutral-900 dark:bg-white text-white dark:text-black'
                            : idx === 1
                              ? 'bg-neutral-200 dark:bg-neutral-700 text-neutral-900 dark:text-white'
                              : idx === 2
                                ? 'bg-neutral-100 dark:bg-neutral-800 text-neutral-700 dark:text-neutral-300'
                                : 'text-neutral-500 dark:text-neutral-400'
                        }`}
                      >
                        {idx + 1}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className="text-sm font-bold text-neutral-900 dark:text-white">{product.name}</span>
                    </td>
                    <td className="px-6 py-4 text-center">
                      <span className="text-sm font-bold text-neutral-900 dark:text-white">
                        {product.total_qty}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-right">
                      <span className="text-base font-black text-neutral-900 dark:text-white">
                        {formatUAH(product.total_revenue)}
                      </span>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
