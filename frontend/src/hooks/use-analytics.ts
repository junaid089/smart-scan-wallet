import { useQuery } from '@tanstack/react-query';
import api from '@/lib/axios';
import { MonthlyAnalytics, SpendingSummary, Expense } from '@/types';

export function useMonthlyAnalytics() {
    return useQuery({
        queryKey: ['analytics', 'monthly'],
        queryFn: async () => {
            const response = await api.get<MonthlyAnalytics>('/analytics/monthly');
            return response.data;
        },
    });
}

export function useSpendingSummary() {
    return useQuery({
        queryKey: ['analytics', 'summary'],
        queryFn: async () => {
            const response = await api.get<SpendingSummary>('/analytics/summary');
            return response.data;
        },
    });
}

export function useExpenses() {
    return useQuery({
        queryKey: ['expenses'],
        queryFn: async () => {
            const response = await api.get<Expense[]>('/receipts/');
            return response.data;
        },
    });
}
