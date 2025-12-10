import React, { useState, useEffect } from 'react';
import { getAgents, createAgent, deleteAgent } from '../api';

function Agents() {
    const [agents, setAgents] = useState([]);
    const [newAgentName, setNewAgentName] = useState('');
    const [newAgentType, setNewAgentType] = useState('coding');
    const [newAgentProvider, setNewAgentProvider] = useState('anthropic');
    const [newAgentModel, setNewAgentModel] = useState('');
    const [availableModels, setAvailableModels] = useState([]);
    const [loadingModels, setLoadingModels] = useState(false);

    useEffect(() => {
        // Fetch models when provider changes
        if (newAgentProvider) {
            setLoadingModels(true);
            fetch(`/api/providers/${newAgentProvider}/models`)
                .then(res => res.json())
                .then(data => {
                    setAvailableModels(data.models || []);
                    if (data.models && data.models.length > 0) {
                        setNewAgentModel(data.models[0]);
                    } else {
                        setNewAgentModel('');
                    }
                    setLoadingModels(false);
                })
                .catch(err => {
                    console.error('Failed to fetch models:', err);
                    setLoadingModels(false);
                    // Fallback to hardcoded
                    const fallback = {
         'anthropic': ['claude-sonnet-4-5-20250929', 'claude-haiku-4-5-20251001', 'claude-opus-4-5-20251101'],
        'openai': ['gpt-5.1', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro'],
        'google': ['gemini-3.0-pro', 'gemini-2.5-pro', 'gemini-2.5-flash'],
        'groq': ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'gemma2-27b-it', 'mixtral-8x7b-32768'],
        'xai': ['grok-4-1-fast-reasoning', 'grok-4-1-fast-non-reasoning', 'grok-code-fast-1','grok-4-fast-reasoning','grok-4-fast-non-reasoning','grok-3-mini','grok-3']
                    }[newAgentProvider] || [];
                    setAvailableModels(fallback);
                    setNewAgentModel(fallback[0] || '');
                });
        }
    }, [newAgentProvider]);

    useEffect(() => {
        fetchAgents();
        const interval = setInterval(fetchAgents, 5000);
        return () => clearInterval(interval);
    }, []);

    const fetchAgents = async () => {
        try {
            const res = await getAgents();
            setAgents(res.data);
        } catch (error) {
            console.error("Failed to fetch agents", error);
        }
    };

    const handleDeleteAgent = async (agentId) => {
      // Check for active jobs first
      try {
        const response = await fetch(`/api/agents/${agentId}/active-jobs`);
        const data = await response.json();
        const activeCount = data.active_jobs_count || 0;

        let confirmMsg = `Delete agent "${agents.find(a => a.id === agentId)?.name}" and its container? This cannot be undone.`;
        if (activeCount > 0) {
          confirmMsg += `\n\nWarning: This agent has ${activeCount} active job(s). Continuing will cancel these jobs.`;
        }

        if (!confirm(confirmMsg)) return;

        // Delete with force if active jobs
        const force = activeCount > 0;
        await deleteAgent(agentId, { force });  // Pass force as query param
        fetchAgents();
      } catch (error) {
        alert('Failed to check/delete agent');
        console.error('Delete error:', error);
      }
    };

    const handleCreateAgent = async (e) => {
        e.preventDefault();
        if (!newAgentName) return;
        try {
            await createAgent({
                name: newAgentName,
                type: newAgentType,
                provider: newAgentProvider,
                model: newAgentModel
            });
            setNewAgentName('');
            setNewAgentModel('');
            fetchAgents();
        } catch (err) {
            alert('Failed to create agent');
        }
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">Agents</h1>
                <span className="bg-blue-100 text-blue-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                    {agents.length} Active
                </span>
            </div>

            <div className="bg-white shadow rounded-lg p-6">
                <h2 className="text-lg font-medium mb-4">Register New Agent</h2>
                <form onSubmit={handleCreateAgent} className="flex flex-wrap gap-4 items-end">
                    <div className="flex-1 min-w-[200px]">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Name</label>
                        <input
                            type="text"
                            value={newAgentName}
                            onChange={(e) => setNewAgentName(e.target.value)}
                            placeholder="e.g. CodeMaster-1"
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                            required
                        />
                    </div>

                    <div className="w-40">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
                        <select
                            value={newAgentType}
                            onChange={(e) => setNewAgentType(e.target.value)}
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            <option value="coding">Coding</option>
                            <option value="architect">Architect</option>
                            <option value="testing">QA / Testing</option>
                            <option value="deployment">Deployment</option>
                            <option value="monitoring">Monitoring</option>
                        </select>
                    </div>

                    <div className="w-40">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
                        <select
                            value={newAgentProvider}
                            onChange={(e) => setNewAgentProvider(e.target.value)}
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            <option value="anthropic">Anthropic</option>
                            <option value="openai">OpenAI</option>
                            <option value="google">Google Gemini</option>
                            <option value="groq">Groq</option>
                            <option value="xai">xAI (Grok)</option>
                        </select>
                    </div>

                    <div className="flex-1 min-w-[200px]">
                        <label className="block text-sm font-medium text-gray-700 mb-1">Model</label>
                        <select
                            value={newAgentModel}
                            onChange={(e) => setNewAgentModel(e.target.value)}
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            {loadingModels ? (
                                <option>Loading models...</option>
                            ) : (
                                availableModels.map(model => (
                                    <option key={model} value={model}>{model}</option>
                                ))
                            )}
                            <option value="custom">Custom...</option>
                        </select>
                    </div>


                    <button type="submit" className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 h-[42px]">
                        Register
                    </button>
                </form>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {agents.map((agent) => (
                    <div key={agent.id} className="bg-white shadow rounded-lg p-6 border border-gray-100 relative overflow-hidden">
                        {/* Status Indicator Stripe */}
                        <div className={`absolute top - 0 left - 0 w - 1 h - full ${agent.status === 'idle' ? 'bg-green-500' :
                                agent.status === 'busy' ? 'bg-yellow-500' :
                                    'bg-gray-300'
                            } `}></div>

                        <div className="flex justify-between items-start mb-4 pl-2">
                            <div>
                                <h3 className="text-lg font-bold text-gray-900">{agent.name}</h3>
                                <p className="text-sm font-medium text-gray-600 capitalize">{agent.type} Agent</p>
                            </div>
                            <span className={`px-2 py-1 rounded-full text-xs font-semibold uppercase ${
                                    agent.status === 'idle' ? 'bg-green-100 text-green-800' :
                                    agent.status === 'busy' ? 'bg-yellow-100 text-yellow-800' :
                                        'bg-gray-100 text-gray-800'
                                }`}>
                                {agent.status}
                            </span>
                            <button
                                onClick={() => handleDeleteAgent(agent.id)}
                                className="ml-3 text-red-500 hover:text-red-700 text-sm font-medium hover:bg-red-50 px-2 py-1 rounded transition-colors"
                                title="Delete agent and container"
                            >
                                Delete
                            </button>
                        </div>

                        <div className="space-y-3 text-sm text-gray-600 pl-2">
                            <div className="flex items-center gap-2">
                                <span className="text-xs font-semibold bg-slate-100 px-2 py-0.5 rounded text-slate-600 border border-slate-200 uppercase">
                                    {agent.provider || 'Anthropic'}
                                </span>
                                {agent.model && <span className="text-xs text-gray-400">({agent.model})</span>}
                            </div>

                            <div className="flex justify-between border-t pt-2 mt-2">
                                <span>Current Job:</span>
                                <span className="font-mono text-blue-600">{agent.current_job_id ? `#${agent.current_job_id} ` : '-'}</span>
                            </div>
                            <div className="flex justify-between">
                                <span>Last Heartbeat:</span>
                                <span className="text-xs text-gray-400">{agent.last_heartbeat ? new Date(agent.last_heartbeat).toLocaleTimeString() : 'Never'}</span>
                            </div>
                        </div>
                    </div>
                ))}

                {agents.length === 0 && (
                    <div className="col-span-full text-center py-12 text-gray-400 bg-gray-50 rounded-lg border-2 border-dashed">
                        No agents registered. Spin one up!
                    </div>
                )}
            </div>
        </div>
    );
}

export default Agents;
