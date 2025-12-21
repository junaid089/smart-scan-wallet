'use client';

import { DollarSign, TrendingUp, Receipt, CreditCard } from 'lucide-react';
import { SpendingCard } from '@/components/dashboard/spending-card';
import { CategoryChart } from '@/components/dashboard/category-chart';
import { useMonthlyAnalytics, useSpendingSummary, useExpenses } from '@/hooks/use-analytics';
import { formatCurrency } from '@/lib/utils';

export default function DashboardPage() {
    const { data: monthlyData, isLoading: isLoadingMonthly } = useMonthlyAnalytics();
    const { data: summaryData, isLoading: isLoadingSummary } = useSpendingSummary();
    const { data: expenses, isLoading: isLoadingExpenses } = useExpenses();

    const isLoading = isLoadingMonthly || isLoadingSummary || isLoadingExpenses;

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white">Dashboard</h1>
                <p className="text-slate-400 mt-1">Track your spending and expenses</p>
            </div>

            {/* Stats Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <SpendingCard
                    title="Total Spending"
                    value={isLoading ? '...' : formatCurrency(summaryData?.total_spending || 0)}
                    icon={DollarSign}
                />
                <SpendingCard
                    title="This Month"
                    value={isLoading ? '...' : formatCurrency(monthlyData?.total_spending || 0)}
                    icon={TrendingUp}
                />
                <SpendingCard
                    title="Total Receipts"
                    value={isLoading ? '...' : String(summaryData?.expense_count || 0)}
                    icon={Receipt}
                />
                <SpendingCard
                    title="Avg Per Expense"
                    value={isLoading ? '...' : formatCurrency(summaryData?.average_per_expense || 0)}
                    icon={CreditCard}
                />
            </div>

            {/* Charts Section */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Pie Chart */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Spending by Category</h2>
                    {isLoadingMonthly ? (
                        <div className="h-[300px] flex items-center justify-center">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500" />
                        </div>
                    ) : (
                        <CategoryChart data={monthlyData?.categories || []} />
                    )}
                </div>

                {/* Recent Expenses */}
                <div className="bg-slate-900/50 border border-slate-800 rounded-xl p-6">
                    <h2 className="text-lg font-semibold text-white mb-4">Recent Expenses</h2>
                    {isLoadingExpenses ? (
                        <div className="h-[300px] flex items-center justify-center">
                            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500" />
                        </div>
                    ) : expenses && expenses.length > 0 ? (
                        <div className="space-y-3 max-h-[300px] overflow-y-auto">
                            {expenses.slice(0, 5).map((expense) => (
                                <div
                                    key={expense.id}
                                    className="flex items-center justify-between p-3 bg-slate-800/50 rounded-lg"
                                >
                                    <div>
                                        <p className="text-white font-medium">{expense.merchant}</p>
                                        <p className="text-sm text-slate-400">{expense.category}</p>
                                    </div>
                                    <p className="text-white font-semibold">
                                        {formatCurrency(expense.amount)}
                                    </p>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="h-[300px] flex items-center justify-center text-slate-500">
                            No expenses yet. Upload a receipt to get started!
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
