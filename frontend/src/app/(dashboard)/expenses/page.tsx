'use client';

import { useExpenses } from '@/hooks/use-analytics';
import { formatCurrency, formatDate, getCategoryColor } from '@/lib/utils';
import { Receipt } from 'lucide-react';

export default function ExpensesPage() {
    const { data: expenses, isLoading } = useExpenses();

    return (
        <div className="space-y-8">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white">My Expenses</h1>
                <p className="text-slate-400 mt-1">View all your scanned receipts and expenses</p>
            </div>

            {/* Expenses Table */}
            <div className="bg-slate-900/50 border border-slate-800 rounded-xl overflow-hidden">
                {isLoading ? (
                    <div className="p-12 text-center">
                        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-500 mx-auto" />
                        <p className="text-slate-400 mt-4">Loading expenses...</p>
                    </div>
                ) : expenses && expenses.length > 0 ? (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="border-b border-slate-800">
                                    <th className="text-left text-sm font-medium text-slate-400 px-6 py-4">Merchant</th>
                                    <th className="text-left text-sm font-medium text-slate-400 px-6 py-4">Category</th>
                                    <th className="text-left text-sm font-medium text-slate-400 px-6 py-4">Date</th>
                                    <th className="text-right text-sm font-medium text-slate-400 px-6 py-4">Amount</th>
                                </tr>
                            </thead>
                            <tbody>
                                {expenses.map((expense) => (
                                    <tr
                                        key={expense.id}
                                        className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-colors"
                                    >
                                        <td className="px-6 py-4">
                                            <div className="flex items-center gap-3">
                                                <div className="w-8 h-8 bg-slate-800 rounded-lg flex items-center justify-center">
                                                    <Receipt className="w-4 h-4 text-slate-400" />
                                                </div>
                                                <span className="text-white font-medium">{expense.merchant}</span>
                                            </div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span
                                                className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium"
                                                style={{
                                                    backgroundColor: `${getCategoryColor(expense.category)}20`,
                                                    color: getCategoryColor(expense.category)
                                                }}
                                            >
                                                {expense.category}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-slate-400">
                                            {formatDate(expense.date)}
                                        </td>
                                        <td className="px-6 py-4 text-right text-white font-semibold">
                                            {formatCurrency(expense.amount)}
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                ) : (
                    <div className="p-12 text-center">
                        <div className="w-16 h-16 bg-slate-800 rounded-full flex items-center justify-center mx-auto mb-4">
                            <Receipt className="w-8 h-8 text-slate-500" />
                        </div>
                        <p className="text-white font-medium mb-1">No expenses yet</p>
                        <p className="text-slate-400 text-sm">Upload a receipt to get started</p>
                    </div>
                )}
            </div>
        </div>
    );
}
