import Cookies from 'js-cookie';
import api from './axios';
import { AuthResponse, User } from '@/types';

const TOKEN_KEY = 'access_token';

export async function login(email: string, password: string): Promise<AuthResponse> {
    // OAuth2 password flow uses form-urlencoded
    const formData = new URLSearchParams();
    formData.append('username', email);
    formData.append('password', password);

    const response = await api.post<AuthResponse>('/auth/login', formData, {
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
    });

    // Store token in cookie
    Cookies.set(TOKEN_KEY, response.data.access_token, {
        expires: 7, // 7 days
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'strict',
    });

    return response.data;
}

export async function register(email: string, password: string): Promise<User> {
    const response = await api.post<User>('/auth/register', {
        email,
        password,
    });

    return response.data;
}

export async function getCurrentUser(): Promise<User> {
    const response = await api.get<User>('/auth/me');
    return response.data;
}

export function logout(): void {
    Cookies.remove(TOKEN_KEY);
    window.location.href = '/login';
}

export function getToken(): string | undefined {
    return Cookies.get(TOKEN_KEY);
}

export function isAuthenticated(): boolean {
    return !!getToken();
}
