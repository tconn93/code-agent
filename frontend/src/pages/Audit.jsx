import React, { useState, useEffect } from 'react';

function Audit() {
    const [auditLogs, setAuditLogs] = useState([]);
    const [loading, setLoading] = useState(true);
    const [filters, setFilters] = useState({
        action: '',
        entity_type: '',
        user: '',
        date_from: '',
        date_to: ''
    });

    // Mock data for demonstration
    useEffect(() => {
        setTimeout(() => {
            setAuditLogs([
                {
                    id: 1,
                    user_id: 1,
                    user_name: 'John Doe',
                    action: 'create',
                    entity_type: 'project',
                    entity_id: 1,
                    entity_name: 'Customer Portal',
                    old_values: null,
                    new_values: { name: 'Customer Portal', status: 'active' },
                    ip_address: '192.168.1.100',
                    created_at: '2024-01-20T14:30:00Z'
                },
                {
                    id: 2,
                    user_id: 2,
                    user_name: 'Jane Smith',
                    action: 'update',
                    entity_type: 'agent',
                    entity_id: 1,
                    entity_name: 'Coding Agent',
                    old_values: { status: 'idle' },
                    new_values: { status: 'busy' },
                    ip_address: '192.168.1.101',
                    created_at: '2024-01-20T14:25:00Z'
                },
                {
                    id: 3,
                    user_id: 1,
                    user_name: 'John Doe',
                    action: 'delete',
                    entity_type: 'job',
                    entity_id: 5,
                    entity_name: 'Job #5',
                    old_values: { status: 'failed' },
                    new_values: null,
                    ip_address: '192.168.1.100',
                    created_at: '2024-01-20T14:20:00Z'
                },
                {
                    id: 4,
                    user_id: 3,
                    user_name: 'Bob Wilson',
                    action: 'approve',
                    entity_type: 'project',
                    entity_id: 2,
                    entity_name: 'API Gateway',
                    old_values: { requires_approval: true },
                    new_values: { approved_by: 3, approved_at: '2024-01-20T14:15:00Z' },
                    ip_address: '192.168.1.102',
                    created_at: '2024-01-20T14:15:00Z'
                }
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    const filteredLogs = auditLogs.filter(log => {
        if (filters.action && log.action !== filters.action) return false;
        if (filters.entity_type && log.entity_type !== filters.entity_type) return false;
        if (filters.user && !log.user_name.toLowerCase().includes(filters.user.toLowerCase())) return false;
        return true;
    });

    const getActionBadge = (action) => {
        const colors = {
            create: 'bg-green-100 text-green-800',
            update: 'bg-blue-100 text-blue-800',
            delete: 'bg-red-100 text-red-800',
            approve: 'bg-purple-100 text-purple-800',
            reject: 'bg-orange-100 text-orange-800'
        };
        return colors[action] || 'bg-gray-100 text-gray-800';
    };

    const getEntityIcon = (entityType) => {
        const icons = {
            project: '📁',
            agent: '🤖',
            job: '⚡',
            user: '👤',
            team: '👥'
        };
        return icons[entityType] || '📄';
    };

    const formatChange = (oldValues, newValues) => {
        if (!oldValues && newValues) {
            return <span className="text-green-600">Created new record</span>;
        }
        if (oldValues && !newValues) {
            return <span className="text-red-600">Deleted record</span>;
        }
        if (oldValues && newValues) {
            const changes = [];
            Object.keys(newValues).forEach(key => {
                if (oldValues[key] !== newValues[key]) {
                    changes.push(`${key}: "${oldValues[key] || 'null'}" → "${newValues[key]}"`);
                }
            });
            return changes.length > 0 ? changes.join(', ') : 'No changes detected';
        }
        return 'Unknown change';
    };

    if (loading) {
        return (
            <div className="flex items-center justify-center h-64">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-slate-900">Audit Log</h1>
                    <p className="text-slate-600 mt-1">Track all system activities and changes</p>
                </div>
                <div className="flex items-center space-x-3">
                    <button className="bg-slate-600 text-white px-4 py-2 rounded-lg hover:bg-slate-700 text-sm">
                        Export CSV
                    </button>
                    <button className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 text-sm">
                        Configure Alerts
                    </button>
                </div>
            </div>

            {/* Filters */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                <h2 className="text-lg font-semibold text-slate-900 mb-4">Filters</h2>
                <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Action</label>
                        <select
                            value={filters.action}
                            onChange={(e) => setFilters({...filters, action: e.target.value})}
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="">All Actions</option>
                            <option value="create">Create</option>
                            <option value="update">Update</option>
                            <option value="delete">Delete</option>
                            <option value="approve">Approve</option>
                            <option value="reject">Reject</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Entity Type</label>
                        <select
                            value={filters.entity_type}
                            onChange={(e) => setFilters({...filters, entity_type: e.target.value})}
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        >
                            <option value="">All Types</option>
                            <option value="project">Project</option>
                            <option value="agent">Agent</option>
                            <option value="job">Job</option>
                            <option value="user">User</option>
                            <option value="team">Team</option>
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">User</label>
                        <input
                            type="text"
                            placeholder="Search by user..."
                            value={filters.user}
                            onChange={(e) => setFilters({...filters, user: e.target.value})}
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">From Date</label>
                        <input
                            type="date"
                            value={filters.date_from}
                            onChange={(e) => setFilters({...filters, date_from: e.target.value})}
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">To Date</label>
                        <input
                            type="date"
                            value={filters.date_to}
                            onChange={(e) => setFilters({...filters, date_to: e.target.value})}
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                </div>
                <div className="mt-4 flex justify-end">
                    <button
                        onClick={() => setFilters({action: '', entity_type: '', user: '', date_from: '', date_to: ''})}
                        className="text-slate-600 hover:text-slate-800 text-sm"
                    >
                        Clear Filters
                    </button>
                </div>
            </div>

            {/* Audit Log Table */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden">
                <div className="px-6 py-4 border-b border-slate-200">
                    <h2 className="text-lg font-semibold text-slate-900">Activity Log ({filteredLogs.length})</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200">
                        <thead className="bg-slate-50">
                            <tr>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Timestamp</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">User</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Action</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Entity</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">Changes</th>
                                <th className="px-6 py-3 text-left text-xs font-medium text-slate-500 uppercase tracking-wider">IP Address</th>
                            </tr>
                        </thead>
                        <tbody className="bg-white divide-y divide-slate-200">
                            {filteredLogs.map((log) => (
                                <tr key={log.id} className="hover:bg-slate-50">
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-900">
                                        {new Date(log.created_at).toLocaleString()}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center mr-3">
                                                <span className="text-xs font-medium text-slate-600">
                                                    {log.user_name.split(' ').map(n => n[0]).join('')}
                                                </span>
                                            </div>
                                            <span className="text-sm font-medium text-slate-900">{log.user_name}</span>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`px-2 py-1 text-xs font-medium rounded-full ${getActionBadge(log.action)}`}>
                                            {log.action}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <div className="flex items-center">
                                            <span className="text-lg mr-2">{getEntityIcon(log.entity_type)}</span>
                                            <div>
                                                <div className="text-sm font-medium text-slate-900">{log.entity_name}</div>
                                                <div className="text-xs text-slate-500 capitalize">{log.entity_type} #{log.entity_id}</div>
                                            </div>
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-slate-500 max-w-xs truncate">
                                        {formatChange(log.old_values, log.new_values)}
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-500">
                                        {log.ip_address}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                    <div className="flex items-center">
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <span className="text-2xl">📊</span>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-slate-600">Total Events</p>
                            <p className="text-2xl font-bold text-slate-900">{auditLogs.length}</p>
                        </div>
                    </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                    <div className="flex items-center">
                        <div className="p-3 bg-green-100 rounded-lg">
                            <span className="text-2xl">✅</span>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-slate-600">Creates</p>
                            <p className="text-2xl font-bold text-slate-900">
                                {auditLogs.filter(log => log.action === 'create').length}
                            </p>
                        </div>
                    </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                    <div className="flex items-center">
                        <div className="p-3 bg-blue-100 rounded-lg">
                            <span className="text-2xl">🔄</span>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-slate-600">Updates</p>
                            <p className="text-2xl font-bold text-slate-900">
                                {auditLogs.filter(log => log.action === 'update').length}
                            </p>
                        </div>
                    </div>
                </div>
                <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                    <div className="flex items-center">
                        <div className="p-3 bg-red-100 rounded-lg">
                            <span className="text-2xl">🗑️</span>
                        </div>
                        <div className="ml-4">
                            <p className="text-sm font-medium text-slate-600">Deletes</p>
                            <p className="text-2xl font-bold text-slate-900">
                                {auditLogs.filter(log => log.action === 'delete').length}
                            </p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default Audit;