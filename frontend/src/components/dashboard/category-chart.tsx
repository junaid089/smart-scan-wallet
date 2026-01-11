'use client';

import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';
import { CategorySpending } from '@/types';

interface CategoryChartProps {
    data: CategorySpending[];
}

export function CategoryChart({ data }: CategoryChartProps) {
    if (!data || data.length === 0) {
        return (
            <div className="h-[300px] flex items-center justify-center text-slate-500">
                No spending data available
            </div>
        );
    }

    const chartData = data.map(item => ({
        name: item.category,
        value: item.amount,
        color: item.color,
    }));

    return (
        <ResponsiveContainer width="100%" height={300}>
            <PieChart>
                <Pie
                    data={chartData}
                    cx="50%"
                    cy="50%"
                    innerRadius={60}
                    outerRadius={100}
                    paddingAngle={2}
                    dataKey="value"
                    label={({ name, percent }) => `${name} ${((percent ?? 0) * 100).toFixed(0)}%`}
                    labelLine={false}
                >
                    {chartData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                </Pie>
                <Tooltip
                    formatter={(value) => [formatCurrency(value as number), 'Amount']}
                    contentStyle={{
                        backgroundColor: '#1e293b',
                        border: '1px solid #334155',
                        borderRadius: '8px',
                        color: '#fff',
                    }}
                />
                <Legend
                    wrapperStyle={{ color: '#94a3b8' }}
                    formatter={(value) => <span className="text-slate-400">{value}</span>}
                />
            </PieChart>
        </ResponsiveContainer>
    );
}
