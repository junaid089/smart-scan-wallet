'use client';

import Link from 'next/link';
import { usePathname } from 'next/navigation';
import {
    LayoutDashboard,
    Upload,
    Receipt,
    MessageSquare,
    LogOut,
    Wallet
} from 'lucide-react';
import { useAuth } from '../auth/auth-provider';
import { cn } from '../../lib/utils';

const navItems = [
    { href: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { href: '/upload', label: 'Upload Receipt', icon: Upload },
    { href: '/expenses', label: 'My Expenses', icon: Receipt },
    { href: '/chat', label: 'AI Chat', icon: MessageSquare },
];

export function Sidebar() {
    const pathname = usePathname();
    const { user, logout } = useAuth();

    return (
        <aside className="fixed left-0 top-0 z-40 h-screen w-64 bg-slate-900 border-r border-slate-800">
            <div className="flex h-full flex-col">
                {/* Logo */}
                <div className="flex items-center gap-3 px-6 py-5 border-b border-slate-800">
                    <div className="p-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-lg">
                        <Wallet className="w-6 h-6 text-white" />
                    </div>
                    <span className="text-lg font-bold text-white">Smart-Scan</span>
                </div>

                {/* Navigation */}
                <nav className="flex-1 px-4 py-6 space-y-1">
                    {navItems.map((item) => {
                        const isActive = pathname === item.href;
                        return (
                            <Link
                                key={item.href}
                                href={item.href}
                                className={cn(
                                    'flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-all',
                                    isActive
                                        ? 'bg-purple-500/20 text-purple-400'
                                        : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                                )}
                            >
                                <item.icon className="w-5 h-5" />
                                {item.label}
                            </Link>
                        );
                    })}
                </nav>

                {/* User section */}
                <div className="border-t border-slate-800 p-4">
                    <div className="flex items-center gap-3 px-2 py-2 mb-2">
                        <div className="w-8 h-8 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center">
                            <span className="text-white text-sm font-medium">
                                {user?.email?.charAt(0).toUpperCase() || 'U'}
                            </span>
                        </div>
                        <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-white truncate">
                                {user?.email || 'User'}
                            </p>
                        </div>
                    </div>
                    <button
                        onClick={logout}
                        className="flex items-center gap-3 w-full px-4 py-2 text-sm text-slate-400 hover:bg-slate-800 hover:text-white rounded-lg transition-all"
                    >
                        <LogOut className="w-4 h-4" />
                        Sign out
                    </button>
                </div>
            </div>
        </aside>
    );
}
