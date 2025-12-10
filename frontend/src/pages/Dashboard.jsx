import React, { useState, useEffect } from 'react';
import { getProjects, getAgents, getJobs } from '../api';

function Dashboard() {
    const [stats, setStats] = useState({
        projects: 0,
        agents: 0,
        jobs: 0,
        activeJobs: 0
    });
    const [recentActivity, setRecentActivity] = useState([]);

    useEffect(() => {
        fetchDashboardData();
    }, []);

    const fetchDashboardData = async () => {
        try {
            const [projectsRes, agentsRes, jobsRes] = await Promise.all([
                getProjects(),
                getAgents(),
                getJobs()
            ]);

            const projects = projectsRes.data || [];
            const agents = agentsRes.data || [];
            const jobs = jobsRes.data || [];

            setStats({
                projects: projects.length,
                agents: agents.length,
                jobs: jobs.length,
                activeJobs: jobs.filter(job => job.status === 'running' || job.status === 'pending').length
            });

            // Get recent activity (last 5 jobs)
            const recentJobs = jobs
                .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
                .slice(0, 5)
                .map(job => ({
                    id: job.id,
                    type: 'job',
                    description: `Job #${job.id} - ${job.type}`,
                    status: job.status,
                    timestamp: job.created_at
                }));

            setRecentActivity(recentJobs);
        } catch (error) {
            console.error('Failed to fetch dashboard data:', error);
        }
    };

    const StatCard = ({ title, value, icon, color, subtitle }) => (
        <div className={`bg-white rounded-lg shadow-sm border border-slate-200 p-6 ${color}`}>
            <div className="flex items-center justify-between">
                <div>
                    <p className="text-sm font-medium text-slate-600">{title}</p>
                    <p className="text-3xl font-bold text-slate-900 mt-1">{value}</p>
                    {subtitle && <p className="text-xs text-slate-500 mt-1">{subtitle}</p>}
                </div>
                <div className="text-4xl opacity-20">{icon}</div>
            </div>
        </div>
    );

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Dashboard</h1>
                    <p className="text-slate-600 mt-1">Welcome back! Here's what's happening with your AI agents.</p>
                </div>
                <div className="flex items-center space-x-3">
                    <div className="flex items-center space-x-2">
                        <div className="w-3 h-3 bg-green-500 rounded-full animate-pulse"></div>
                        <span className="text-sm text-slate-600">All Systems Operational</span>
                    </div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <StatCard
                    title="Total Projects"
                    value={stats.projects}
                    icon="📁"
                    color="hover:shadow-md"
                    subtitle="Active development projects"
                />
                <StatCard
                    title="AI Agents"
                    value={stats.agents}
                    icon="🤖"
                    color="hover:shadow-md"
                    subtitle="Configured and ready"
                />
                <StatCard
                    title="Total Jobs"
                    value={stats.jobs}
                    icon="⚡"
                    color="hover:shadow-md"
                    subtitle="Tasks processed"
                />
                <StatCard
                    title="Active Jobs"
                    value={stats.activeJobs}
                    icon="🔄"
                    color="hover:shadow-md"
                    subtitle="Currently running"
                />
            </div>

            {/* Recent Activity */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200">
                <div className="px-6 py-4 border-b border-slate-200">
                    <h2 className="text-lg font-semibold text-slate-900">Recent Activity</h2>
                    <p className="text-sm text-slate-600">Latest jobs and system events</p>
                </div>
                <div className="divide-y divide-slate-200">
                    {recentActivity.length > 0 ? (
                        recentActivity.map((activity) => (
                            <div key={activity.id} className="px-6 py-4 flex items-center justify-between hover:bg-slate-50">
                                <div className="flex items-center space-x-3">
                                    <div className={`w-2 h-2 rounded-full ${
                                        activity.status === 'completed' ? 'bg-green-500' :
                                        activity.status === 'failed' ? 'bg-red-500' :
                                        activity.status === 'running' ? 'bg-blue-500' :
                                        'bg-yellow-500'
                                    }`}></div>
                                    <div>
                                        <p className="text-sm font-medium text-slate-900">{activity.description}</p>
                                        <p className="text-xs text-slate-500">
                                            {new Date(activity.timestamp).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                    activity.status === 'completed' ? 'bg-green-100 text-green-800' :
                                    activity.status === 'failed' ? 'bg-red-100 text-red-800' :
                                    activity.status === 'running' ? 'bg-blue-100 text-blue-800' :
                                    'bg-yellow-100 text-yellow-800'
                                }`}>
                                    {activity.status}
                                </span>
                            </div>
                        ))
                    ) : (
                        <div className="px-6 py-8 text-center">
                            <p className="text-slate-500">No recent activity</p>
                        </div>
                    )}
                </div>
            </div>

            {/* Quick Actions */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Quick Actions</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <button className="flex items-center justify-center px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
                        <span className="mr-2">📁</span>
                        Create Project
                    </button>
                    <button className="flex items-center justify-center px-4 py-3 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors">
                        <span className="mr-2">🤖</span>
                        Deploy Agent
                    </button>
                    <button className="flex items-center justify-center px-4 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors">
                        <span className="mr-2">📊</span>
                        View Reports
                    </button>
                </div>
            </div>
        </div>
    );
}

export default Dashboard;