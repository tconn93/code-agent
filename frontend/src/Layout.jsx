import React, { useState } from 'react';
import { Outlet, Link, useLocation } from 'react-router-dom';

function Layout() {
    const location = useLocation();
    const [sidebarOpen, setSidebarOpen] = useState(false);

    const navItems = [
        { label: 'Dashboard', path: '/', icon: '📊' },
        { label: 'Projects', path: '/projects', icon: '📁' },
        { label: 'Agents', path: '/agents', icon: '🤖' },
        { label: 'Jobs', path: '/jobs', icon: '⚡' },
        { label: 'Users', path: '/users', icon: '👥' },
        { label: 'Teams', path: '/teams', icon: '🏢' },
        { label: 'Audit', path: '/audit', icon: '📋' },
        { label: 'Settings', path: '/settings', icon: '⚙️' },
    ];

    const isActive = (path) => {
        if (path === '/' && location.pathname === '/') return true;
        if (path !== '/' && location.pathname.startsWith(path)) return true;
        return false;
    };

    return (
        <div className="min-h-screen bg-slate-50 font-sans">
            {/* Top Navigation Bar */}
            <nav className="bg-white border-b border-slate-200 sticky top-0 z-40 shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between h-16">
                        <div className="flex items-center">
                            <button
                                onClick={() => setSidebarOpen(!sidebarOpen)}
                                className="md:hidden p-2 rounded-md text-slate-400 hover:text-slate-500 hover:bg-slate-100"
                            >
                                <span className="sr-only">Open sidebar</span>
                                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                                </svg>
                            </button>
                            <div className="flex-shrink-0 flex items-center ml-4 md:ml-0">
                                <div className="flex items-center space-x-3">
                                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
                                        <span className="text-white font-bold text-sm">AI</span>
                                    </div>
                                    <div>
                                        <h1 className="text-lg font-semibold text-slate-900">Enterprise AI Platform</h1>
                                        <p className="text-xs text-slate-500">Intelligent Automation Suite</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div className="flex items-center space-x-4">
                            <div className="hidden md:flex items-center space-x-2">
                                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                                <span className="text-sm text-slate-600">System Online</span>
                            </div>
                            <div className="flex items-center space-x-3">
                                <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                                    <span className="text-sm font-medium text-slate-600">JD</span>
                                </div>
                                <span className="hidden md:block text-sm font-medium text-slate-700">John Doe</span>
                            </div>
                        </div>
                    </div>
                </div>
            </nav>

            <div className="flex">
                {/* Sidebar */}
                <div className={`fixed inset-y-0 left-0 z-50 w-64 bg-white border-r border-slate-200 transform ${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:inset-0`}>
                    <div className="flex flex-col h-full pt-16 md:pt-0">
                        <nav className="flex-1 px-4 py-6 space-y-2">
                            {navItems.map((item) => (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setSidebarOpen(false)}
                                    className={`group flex items-center px-3 py-2 text-sm font-medium rounded-lg transition-colors duration-150 ${
                                        isActive(item.path)
                                            ? 'bg-blue-50 text-blue-700 border-r-2 border-blue-600'
                                            : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900'
                                    }`}
                                >
                                    <span className="mr-3 text-lg">{item.icon}</span>
                                    {item.label}
                                    {isActive(item.path) && (
                                        <span className="ml-auto w-2 h-2 bg-blue-600 rounded-full"></span>
                                    )}
                                </Link>
                            ))}
                        </nav>

                        {/* Sidebar Footer */}
                        <div className="p-4 border-t border-slate-200">
                            <div className="flex items-center space-x-3">
                                <div className="flex-1">
                                    <p className="text-xs text-slate-500">Version 2.1.0</p>
                                    <p className="text-xs text-slate-400">Enterprise Edition</p>
                                </div>
                                <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Overlay for mobile */}
                {sidebarOpen && (
                    <div
                        className="fixed inset-0 z-40 bg-black bg-opacity-50 md:hidden"
                        onClick={() => setSidebarOpen(false)}
                    ></div>
                )}

                {/* Main Content */}
                <div className="flex-1 md:ml-0">
                    <main className="p-6">
                        <Outlet />
                    </main>
                </div>
            </div>
        </div>
    );
}

export default Layout;
