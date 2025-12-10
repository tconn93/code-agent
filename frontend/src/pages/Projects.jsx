import React, { useState, useEffect } from 'react';
import { getProjects, createProject, getJobs, createJob, getUsers, getTeams, getAgents } from '../api';

function Projects() {
    const [projects, setProjects] = useState([]);
    const [selectedProject, setSelectedProject] = useState(null);
    const [jobs, setJobs] = useState([]);

    const [newProjectName, setNewProjectName] = useState('');
    const [newProjectDesc, setNewProjectDesc] = useState('');
    const [newProjectRepo, setNewProjectRepo] = useState('');
    const [newTask, setNewTask] = useState('');
    const [selectedAgentId, setSelectedAgentId] = useState(null);  // For job assignment
    const [selectedJobType, setSelectedJobType] = useState('implement_feature');

    const [users, setUsers] = useState([]);
    const [teams, setTeams] = useState([]);
    const [agents, setAgents] = useState([]);  // For job assignment

    const [newProjectOwnerId, setNewProjectOwnerId] = useState('');
    const [newProjectTeamId, setNewProjectTeamId] = useState('');
    const [newProjectDepartment, setNewProjectDepartment] = useState('');
    const [newProjectStatus, setNewProjectStatus] = useState('active');
    const [newProjectPriority, setNewProjectPriority] = useState('medium');
    const [newProjectSecurityLevel, setNewProjectSecurityLevel] = useState('internal');
    const [newProjectBudget, setNewProjectBudget] = useState('');
    const [newProjectRequiresApproval, setNewProjectRequiresApproval] = useState(false);

useEffect(() => {
    fetchProjects();
    fetchUsers();
    fetchTeams();
    fetchAgents();  // Load agents for job assignment
  }, []);

    useEffect(() => {
        if (selectedProject && selectedProject !== 'new') {
            fetchJobs(selectedProject.id);
            const interval = setInterval(() => fetchJobs(selectedProject.id), 3000);
            return () => clearInterval(interval);
        }
    }, [selectedProject]);

    const fetchProjects = async () => {
        const res = await getProjects();
        setProjects(res.data);
    };

  const fetchJobs = async (projectId) => {
    const res = await getJobs(projectId);
    setJobs(res.data);
  };

  const fetchUsers = async () => {
    try {
      const res = await getUsers();
      setUsers(res.data || []);
    } catch (err) {
      console.error('Failed to fetch users');
    }
  };

    const fetchTeams = async () => {
        try {
          const res = await getTeams();
          setTeams(res.data || []);
        } catch (err) {
          console.error('Failed to fetch teams');
        }
    };

    const fetchAgents = async () => {
        try {
          const res = await getAgents();
          setAgents(res.data || []);
        } catch (err) {
          console.error('Failed to fetch agents');
        }
    };

    const handleCreateProject = async (e) => {
        e.preventDefault();
        if (!newProjectName) return;
        try {
            const res = await createProject({
                name: newProjectName,
                description: newProjectDesc,
                repo_url: newProjectRepo,
                owner_id: newProjectOwnerId ? parseInt(newProjectOwnerId) : null,
                team_id: newProjectTeamId ? parseInt(newProjectTeamId) : null,
                department: newProjectDepartment || null,
                status: newProjectStatus,
                priority: newProjectPriority,
                security_level: newProjectSecurityLevel,
                budget_allocated: newProjectBudget ? parseFloat(newProjectBudget) : null,
                requires_approval: newProjectRequiresApproval
            });
            setNewProjectName('');
            setNewProjectDesc('');
            setNewProjectRepo('');
            setNewProjectOwnerId('');
            setNewProjectTeamId('');
            setNewProjectDepartment('');
            setNewProjectStatus('active');
            setNewProjectPriority('medium');
            setNewProjectSecurityLevel('internal');
            setNewProjectBudget('');
            setNewProjectRequiresApproval(false);
            await fetchProjects();
            setSelectedProject(res.data);
        } catch (err) {
            alert('Failed to create project');
        }
    };

    const handleCreateJob = async (e) => {
        e.preventDefault();
        if (!newTask || !selectedProject || selectedProject === 'new') return;
        try {
            await createJob({
                project_id: selectedProject.id,
                type: selectedJobType,
                payload: { task: newTask },
                assigned_agent_id: selectedAgentId  // Assign to selected agent
            });
            setNewTask('');
            setSelectedAgentId(null);
            fetchJobs(selectedProject.id);
        } catch (err) {
            alert('Failed to create job');
        }
    };

    return (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            {/* Sidebar */}
            <div className="md:col-span-1 bg-white p-4 rounded-lg shadow h-fit">
                <div className="flex justify-between items-center mb-4">
                    <h2 className="text-xl font-semibold">Projects</h2>
                    <button
                        onClick={() => setSelectedProject('new')}
                        className="bg-blue-600 text-white px-3 py-1 rounded text-sm hover:bg-blue-700"
                    >
                        + New
                    </button>
                </div>

                <ul className="space-y-2">
                    {projects.map((p) => (
                        <li
                            key={p.id}
                            onClick={() => setSelectedProject(p)}
                            className={`p-3 rounded cursor-pointer transition-colors ${selectedProject?.id === p.id ? 'bg-blue-50 text-blue-700 border border-blue-200' : 'hover:bg-gray-50'}`}
                        >
                            <div className="font-medium">{p.name}</div>
                            <div className="text-xs text-gray-400 truncate">{p.description || 'No description'}</div>
                        </li>
                    ))}
                </ul>
            </div>

            {/* Main Content Area */}
            <div className="md:col-span-3">
                {selectedProject === 'new' && (
                    <div className="bg-white p-8 rounded-lg shadow">
                        <h2 className="text-2xl font-bold mb-6">Create New Project</h2>
                        <form onSubmit={handleCreateProject} className="space-y-4 max-w-lg">
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Project Name *</label>
                                <input
                                    type="text"
                                    required
                                    value={newProjectName}
                                    onChange={(e) => setNewProjectName(e.target.value)}
                                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
                                <textarea
                                    value={newProjectDesc}
                                    onChange={(e) => setNewProjectDesc(e.target.value)}
                                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none h-24"
                                />
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Repository URL</label>
                                <input
                                    type="text"
                                    value={newProjectRepo}
                                    onChange={(e) => setNewProjectRepo(e.target.value)}
                                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>

                            {/* New Enterprise Fields */}
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Owner</label>
                                <select
                                    value={newProjectOwnerId}
                                    onChange={(e) => setNewProjectOwnerId(e.target.value)}
                                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                >
                                    <option value="">Select Owner</option>
                                    {users.map((user) => (
                                        <option key={user.id} value={user.id}>
                                            {user.name} ({user.email})
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Team</label>
                                <select
                                    value={newProjectTeamId}
                                    onChange={(e) => setNewProjectTeamId(e.target.value)}
                                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                >
                                    <option value="">Select Team</option>
                                    {teams.map((team) => (
                                        <option key={team.id} value={team.id}>
                                            {team.name}
                                        </option>
                                    ))}
                                </select>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-gray-700 mb-1">Department</label>
                                <input
                                    type="text"
                                    value={newProjectDepartment}
                                    onChange={(e) => setNewProjectDepartment(e.target.value)}
                                    className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
                                    <select 
                                        value={newProjectStatus} 
                                        onChange={(e) => setNewProjectStatus(e.target.value)} 
                                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    >
                                        <option value="active">Active</option>
                                        <option value="paused">Paused</option>
                                        <option value="completed">Completed</option>
                                        <option value="archived">Archived</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Priority</label>
                                    <select 
                                        value={newProjectPriority} 
                                        onChange={(e) => setNewProjectPriority(e.target.value)} 
                                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    >
                                        <option value="low">Low</option>
                                        <option value="medium">Medium</option>
                                        <option value="high">High</option>
                                        <option value="critical">Critical</option>
                                    </select>
                                </div>
                            </div>
                            <div className="grid grid-cols-2 gap-4">
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Security Level</label>
                                    <select 
                                        value={newProjectSecurityLevel} 
                                        onChange={(e) => setNewProjectSecurityLevel(e.target.value)} 
                                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    >
                                        <option value="public">Public</option>
                                        <option value="internal">Internal</option>
                                        <option value="confidential">Confidential</option>
                                        <option value="restricted">Restricted</option>
                                    </select>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Budget ($)</label>
                                    <input
                                        type="number"
                                        step="0.01"
                                        value={newProjectBudget}
                                        onChange={(e) => setNewProjectBudget(e.target.value)}
                                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    />
                                </div>
                            </div>
                            <div className="flex items-center">
                                <input
                                    type="checkbox"
                                    id="requiresApproval"
                                    checked={newProjectRequiresApproval}
                                    onChange={(e) => setNewProjectRequiresApproval(e.target.checked)}
                                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                                />
                                <label htmlFor="requiresApproval" className="ml-2 block text-sm text-gray-900">
                                    Requires Approval
                                </label>
                            </div>

                            <div className="pt-4">
                                <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700">Create Project</button>
                                <button type="button" onClick={() => setSelectedProject(null)} className="ml-4 text-gray-500 hover:text-gray-700">Cancel</button>
                            </div>
                        </form>
                    </div>
                )}

                {selectedProject && selectedProject !== 'new' && (
                    <div>
                        <div className="flex justify-between items-center mb-6">
                            <div>
                                <h2 className="text-2xl font-bold">{selectedProject.name}</h2>
                                <p className="text-gray-600 mt-1">{selectedProject.description}</p>
                                <p className="text-gray-400 text-sm mt-1">{selectedProject.repo_url}</p>
                                {selectedProject.department && (
                                    <p className="text-gray-400 text-sm mt-1">Department: {selectedProject.department}</p>
                                )}
                                {selectedProject.status && (
                                    <span className={`inline-block px-2 py-1 rounded text-xs font-bold uppercase ${
                                        selectedProject.status === 'active' ? 'bg-green-100 text-green-800' :
                                        selectedProject.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
                                        selectedProject.status === 'completed' ? 'bg-blue-100 text-blue-800' :
                                        'bg-gray-100 text-gray-800'
                                    }`}>
                                        {selectedProject.status}
                                    </span>
                                )}
                                {selectedProject.priority && (
                                    <p className="text-gray-400 text-sm mt-1">Priority: {selectedProject.priority}</p>
                                )}
                                {selectedProject.security_level && (
                                    <p className="text-gray-400 text-sm mt-1">Security: {selectedProject.security_level}</p>
                                )}
                                {selectedProject.budget_allocated && (
                                    <p className="text-gray-400 text-sm mt-1">Budget: ${selectedProject.budget_allocated}</p>
                                )}
                                {selectedProject.requires_approval && (
                                    <p className="text-gray-400 text-sm mt-1">Requires Approval: Yes</p>
                                )}
                            </div>
                        </div>

                        <div className="bg-white p-6 rounded-lg shadow mb-8">
                            <h3 className="text-lg font-semibold mb-2">New Mission</h3>
                            <form onSubmit={handleCreateJob} className="flex flex-wrap gap-4 items-end">
                                <input
                                    type="text"
                                    value={newTask}
                                    onChange={(e) => setNewTask(e.target.value)}
                                    placeholder="Describe the task..."
                                    className="flex-1 min-w-[200px] p-3 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                />
                                <div className="w-48">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Job Type</label>
                                    <select
                                        value={selectedJobType}
                                        onChange={(e) => setSelectedJobType(e.target.value)}
                                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    >
                                        <option value="design_system">Design System</option>
                                        <option value="review_architecture">Review Architecture</option>
                                        <option value="implement_feature">Implement Feature</option>
                                        <option value="review_code">Review Code</option>
                                        <option value="create_tests">Create Tests</option>
                                        <option value="run_qa_suite">Run QA Suite</option>
                                        <option value="setup_deployment">Setup Deployment</option>
                                        <option value="execute_deployment">Execute Deployment</option>
                                        <option value="setup_monitoring">Setup Monitoring</option>
                                        <option value="perform_health_audit">Perform Health Audit</option>
                                    </select>
                                </div>
                                <div className="w-64">
                                    <label className="block text-sm font-medium text-gray-700 mb-1">Assign Agent</label>
                                    <select
                                        value={selectedAgentId || ''}
                                        onChange={(e) => setSelectedAgentId(e.target.value ? parseInt(e.target.value) : null)}
                                        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                                    >
                                        <option value="">Auto-assign (default)</option>
                                        {agents.filter(a => a.status === 'idle').map((agent) => (
                                            <option key={agent.id} value={agent.id}>
                                                {agent.name} ({agent.provider} - {agent.type})
                                            </option>
                                        ))}
                                    </select>
                                </div>
                                <button type="submit" className="bg-green-600 text-white px-6 py-3 rounded font-medium hover:bg-green-700">Dispatch</button>
                            </form>
                        </div>

                        <h3 className="text-xl font-semibold mb-4">Activity Log</h3>
                        <div className="space-y-4">
                            {jobs.slice().reverse().map((job) => (
                                <div key={job.id} className="bg-white p-6 rounded-lg shadow border border-gray-100">
                                    <div className="flex justify-between items-start mb-2">
                                        <div className="flex items-center gap-2">
                                            <span className={`px-2 py-1 rounded text-xs font-bold uppercase ${job.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                    job.status === 'failed' ? 'bg-red-100 text-red-800' :
                                                        'bg-gray-100 text-gray-800'
                                                }`}>
                                                {job.status}
                                            </span>
                                            <span className="text-sm text-gray-500">Job #{job.id} • {job.type}</span>
                                        </div>
                                        <span className="text-xs text-gray-400">{new Date(job.created_at).toLocaleString()}</span>
                                    </div>
                                    <div className="bg-gray-50 p-3 rounded text-sm text-gray-700 mb-4 font-mono whitespace-pre-wrap">{job.payload.task}</div>
                                    {(job.result || job.logs) && (
                                        <div className="border-t pt-4 mt-2">
                                            <pre className="bg-slate-900 text-slate-50 p-4 rounded overflow-x-auto text-xs font-mono">{JSON.stringify(job.result || job.logs, null, 2)}</pre>
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}

export default Projects;
