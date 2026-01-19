import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart, Line, LineChart } from 'recharts';

interface OrdersChartProps {
  data: Array<{ date: string; orders: number }>;
}

export default function OrdersChart({ data }: OrdersChartProps) {
  return (
    <div className="w-full" style={{ minWidth: 0, minHeight: 320, height: 320 }}>
      <ResponsiveContainer width="100%" height={320} minHeight={320}>
        <AreaChart data={data} margin={{ top: 15, right: 25, left: 5, bottom: 10 }}>
          <defs>
            <linearGradient id="colorOrdersGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#171717" stopOpacity={0.25} />
              <stop offset="50%" stopColor="#404040" stopOpacity={0.15} />
              <stop offset="100%" stopColor="#171717" stopOpacity={0} />
            </linearGradient>
            <linearGradient id="colorOrdersLine" x1="0" y1="0" x2="1" y2="0">
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
            dataKey="date" 
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
            width={35}
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
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '6px',
            }}
            itemStyle={{ 
              color: '#404040', 
              fontSize: '13px',
              fontWeight: '600',
            }}
            cursor={{ stroke: '#171717', strokeWidth: 2, strokeDasharray: '3 3' }}
          />
          <Area
            type="monotone"
            dataKey="orders"
            stroke="url(#colorOrdersLine)"
            strokeWidth={2.5}
            fillOpacity={1}
            fill="url(#colorOrdersGradient)"
            dot={{ fill: '#171717', strokeWidth: 2, r: 4 }}
            activeDot={{ r: 6, stroke: '#171717', strokeWidth: 2, fill: '#ffffff' }}
            isAnimationActive={false}
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}

