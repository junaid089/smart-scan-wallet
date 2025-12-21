import { Sidebar } from '../../components/layout/sidebar';

export default function DashboardLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return (
        <div className="min-h-screen bg-slate-950">
            <Sidebar />
            <main className="ml-64 min-h-screen">
                <div className="p-8">
                    {children}
                </div>
            </main>
        </div>
    );
}
