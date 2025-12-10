import React, { useState, useEffect } from 'react';

function Teams() {
    const [teams, setTeams] = useState([]);
    const [loading, setLoading] = useState(true);
    const [searchTerm, setSearchTerm] = useState('');
    const [showCreateModal, setShowCreateModal] = useState(false);
    const [selectedTeam, setSelectedTeam] = useState(null);
    const [showMembersModal, setShowMembersModal] = useState(false);

    // Mock data for demonstration
    useEffect(() => {
        setTimeout(() => {
            setTeams([
                {
                    id: 1,
                    name: 'Frontend Team',
                    description: 'React and UI development team',
                    department: 'Engineering',
                    manager_id: 1,
                    manager_name: 'John Doe',
                    member_count: 5,
                    budget_allocated: 150000,
                    is_active: true,
                    created_at: '2024-01-10T09:00:00Z'
                },
                {
                    id: 2,
                    name: 'Backend Team',
                    description: 'API and database development',
                    department: 'Engineering',
                    manager_id: 2,
                    manager_name: 'Jane Smith',
                    member_count: 4,
                    budget_allocated: 120000,
                    is_active: true,
                    created_at: '2024-01-12T10:30:00Z'
                },
                {
                    id: 3,
                    name: 'DevOps Team',
                    description: 'Infrastructure and deployment',
                    department: 'Operations',
                    manager_id: 3,
                    manager_name: 'Bob Wilson',
                    member_count: 3,
                    budget_allocated: 100000,
                    is_active: false,
                    created_at: '2024-01-15T14:20:00Z'
                }
            ]);
            setLoading(false);
        }, 1000);
    }, []);

    const filteredTeams = teams.filter(team =>
        team.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        team.description.toLowerCase().includes(searchTerm.toLowerCase()) ||
        team.department.toLowerCase().includes(searchTerm.toLowerCase())
    );

    const TeamModal = ({ team, onClose }) => (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-lg w-full mx-4">
                <div className="px-6 py-4 border-b border-slate-200">
                    <h3 className="text-lg font-semibold text-slate-900">
                        {team ? 'Edit Team' : 'Create Team'}
                    </h3>
                </div>
                <div className="px-6 py-4 space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Team Name</label>
                        <input
                            type="text"
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            defaultValue={team?.name || ''}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Description</label>
                        <textarea
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 h-24"
                            defaultValue={team?.description || ''}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Department</label>
                        <input
                            type="text"
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            defaultValue={team?.department || ''}
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-slate-700 mb-1">Budget Allocated ($)</label>
                        <input
                            type="number"
                            className="w-full px-3 py-2 border border-slate-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                            defaultValue={team?.budget_allocated || ''}
                        />
                    </div>
                </div>
                <div className="px-6 py-4 border-t border-slate-200 flex justify-end space-x-3">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200"
                    >
                        Cancel
                    </button>
                    <button className="px-4 py-2 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700">
                        {team ? 'Update' : 'Create'}
                    </button>
                </div>
            </div>
        </div>
    );

    const MembersModal = ({ team, onClose }) => (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4">
                <div className="px-6 py-4 border-b border-slate-200">
                    <h3 className="text-lg font-semibold text-slate-900">
                        {team.name} - Team Members
                    </h3>
                </div>
                <div className="px-6 py-4">
                    <div className="space-y-3">
                        {/* Mock team members */}
                        {[
                            { name: 'Alice Johnson', role: 'Senior Developer', email: 'alice@company.com' },
                            { name: 'Charlie Brown', role: 'Developer', email: 'charlie@company.com' },
                            { name: 'Diana Prince', role: 'UI Designer', email: 'diana@company.com' },
                            { name: 'Eve Wilson', role: 'QA Engineer', email: 'eve@company.com' },
                            { name: 'Frank Miller', role: 'DevOps Engineer', email: 'frank@company.com' }
                        ].map((member, index) => (
                            <div key={index} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                                <div className="flex items-center space-x-3">
                                    <div className="w-8 h-8 bg-slate-200 rounded-full flex items-center justify-center">
                                        <span className="text-xs font-medium text-slate-600">
                                            {member.name.split(' ').map(n => n[0]).join('')}
                                        </span>
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-slate-900">{member.name}</p>
                                        <p className="text-xs text-slate-500">{member.role} • {member.email}</p>
                                    </div>
                                </div>
                                <button className="text-red-600 hover:text-red-800 text-sm">Remove</button>
                            </div>
                        ))}
                    </div>
                    <div className="mt-4 pt-4 border-t border-slate-200">
                        <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700">
                            Add Team Member
                        </button>
                    </div>
                </div>
                <div className="px-6 py-4 border-t border-slate-200 flex justify-end">
                    <button
                        onClick={onClose}
                        className="px-4 py-2 text-sm font-medium text-slate-700 bg-slate-100 rounded-md hover:bg-slate-200"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );

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
                    <h1 className="text-3xl font-bold text-slate-900">Team Management</h1>
                    <p className="text-slate-600 mt-1">Organize teams and manage resources</p>
                </div>
                <button
                    onClick={() => setShowCreateModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 flex items-center space-x-2"
                >
                    <span>+</span>
                    <span>Create Team</span>
                </button>
            </div>

            {/* Search and Filters */}
            <div className="bg-white rounded-lg shadow-sm border border-slate-200 p-6">
                <div className="flex items-center space-x-4">
                    <div className="flex-1">
                        <input
                            type="text"
                            placeholder="Search teams by name, description, or department..."
                            value={searchTerm}
                            onChange={(e) => setSearchTerm(e.target.value)}
                            className="w-full px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                    </div>
                    <select className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">All Departments</option>
                        <option value="Engineering">Engineering</option>
                        <option value="Product">Product</option>
                        <option value="Operations">Operations</option>
                        <option value="Design">Design</option>
                    </select>
                    <select className="px-4 py-2 border border-slate-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
                        <option value="">All Status</option>
                        <option value="active">Active</option>
                        <option value="inactive">Inactive</option>
                    </select>
                </div>
            </div>

            {/* Teams Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {filteredTeams.map((team) => (
                    <div key={team.id} className="bg-white rounded-lg shadow-sm border border-slate-200 overflow-hidden hover:shadow-md transition-shadow">
                        <div className="p-6">
                            <div className="flex items-start justify-between mb-4">
                                <div className="flex items-center space-x-3">
                                    <div className="w-12 h-12 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
                                        <span className="text-white font-bold text-lg">
                                            {team.name.split(' ').map(word => word[0]).join('').toUpperCase()}
                                        </span>
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-semibold text-slate-900">{team.name}</h3>
                                        <p className="text-sm text-slate-500">{team.department}</p>
                                    </div>
                                </div>
                                <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                                    team.is_active
                                        ? 'bg-green-100 text-green-800'
                                        : 'bg-red-100 text-red-800'
                                }`}>
                                    {team.is_active ? 'Active' : 'Inactive'}
                                </span>
                            </div>

                            <p className="text-slate-600 text-sm mb-4 line-clamp-2">{team.description}</p>

                            <div className="space-y-2 mb-4">
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-500">Manager:</span>
                                    <span className="text-slate-900">{team.manager_name}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-500">Members:</span>
                                    <span className="text-slate-900">{team.member_count}</span>
                                </div>
                                <div className="flex justify-between text-sm">
                                    <span className="text-slate-500">Budget:</span>
                                    <span className="text-slate-900">${team.budget_allocated?.toLocaleString()}</span>
                                </div>
                            </div>

                            <div className="flex space-x-2">
                                <button
                                    onClick={() => setSelectedTeam(team)}
                                    className="flex-1 bg-slate-100 text-slate-700 py-2 px-3 rounded-md hover:bg-slate-200 text-sm font-medium"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => {
                                        setSelectedTeam(team);
                                        setShowMembersModal(true);
                                    }}
                                    className="flex-1 bg-blue-600 text-white py-2 px-3 rounded-md hover:bg-blue-700 text-sm font-medium"
                                >
                                    Members
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>

            {/* Modals */}
            {showCreateModal && (
                <TeamModal onClose={() => setShowCreateModal(false)} />
            )}
            {selectedTeam && !showMembersModal && (
                <TeamModal team={selectedTeam} onClose={() => setSelectedTeam(null)} />
            )}
            {showMembersModal && selectedTeam && (
                <MembersModal team={selectedTeam} onClose={() => {
                    setShowMembersModal(false);
                    setSelectedTeam(null);
                }} />
            )}
        </div>
    );
}

export default Teams;