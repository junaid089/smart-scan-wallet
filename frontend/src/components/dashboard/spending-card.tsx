import { LucideIcon } from 'lucide-react';
import { cn } from '../../lib/utils';

interface SpendingCardProps {
    title: string;
    value: string;
    icon: LucideIcon;
    trend?: {
        value: number;
        isPositive: boolean;
    };
    className?: string;
}

export function SpendingCard({ title, value, icon: Icon, trend, className }: SpendingCardProps) {
    return (
        <div className={cn(
            "bg-slate-900/50 border border-slate-800 rounded-xl p-6",
            className
        )}>
            <div className="flex items-center justify-between mb-4">
                <p className="text-sm font-medium text-slate-400">{title}</p>
                <div className="p-2 bg-purple-500/20 rounded-lg">
                    <Icon className="w-5 h-5 text-purple-400" />
                </div>
            </div>
            <p className="text-2xl font-bold text-white mb-1">{value}</p>
            {trend && (
                <p className={cn(
                    "text-sm font-medium",
                    trend.isPositive ? "text-green-400" : "text-red-400"
                )}>
                    {trend.isPositive ? '↑' : '↓'} {Math.abs(trend.value)}% from last month
                </p>
            )}
        </div>
    );
}
