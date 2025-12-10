import React, { useState, useEffect } from 'react';
import { getSettings, saveSetting } from '../api';

function Settings() {
    const [settings, setSettings] = useState([]);
    const [loading, setLoading] = useState(false);

    // LLM Provider state
    const [providers, setProviders] = useState({
        anthropic: { key: '', models: [] },
        openai: { key: '', models: [] },
        google: { key: '', models: [] },
        groq: { key: '', models: [] },
        xai: { key: '', models: [] }
    });
    const [defaultProvider, setDefaultProvider] = useState('anthropic');
    const [defaultModel, setDefaultModel] = useState('');
    const [availableModels, setAvailableModels] = useState([]);

    // Specific known keys we want to manage easily, though the DB is generic
    const [newKey, setNewKey] = useState('');
    const [newValue, setNewValue] = useState('');
    const [newCategory, setNewCategory] = useState('general');

    // Predefined models for each provider
    const providerModels = {
        anthropic: ['claude-sonnet-4-5-20250929', 'claude-haiku-4-5-20251001', 'claude-opus-4-5-20251101'],
        openai: ['gpt-5.1', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro'],
        google: ['gemini-3.0-pro', 'gemini-2.5-pro', 'gemini-2.5-flash'],
        groq: ['llama-3.3-70b-versatile', 'llama-3.1-8b-instant', 'gemma2-27b-it', 'mixtral-8x7b-32768'],
        xai: ['grok-4-1-fast-reasoning', 'grok-4-1-fast-non-reasoning', 'grok-code-fast-1','grok-4-fast-reasoning','grok-4-fast-non-reasoning','grok-3-mini','grok-3']
    };

    useEffect(() => {
        fetchSettings();
    }, []);

    useEffect(() => {
        // Update available models when default provider changes
        setAvailableModels(providerModels[defaultProvider] || []);
        if (providerModels[defaultProvider]?.length > 0) {
            setDefaultModel(providerModels[defaultProvider][0]);
        }
    }, [defaultProvider]);

    const fetchSettings = async () => {
        try {
            const res = await getSettings();
            setSettings(res.data);

            // Parse LLM provider settings
            const newProviders = { ...providers };
            res.data.forEach(setting => {
                if (setting.key === 'ANTHROPIC_API_KEY') {
                    newProviders.anthropic.key = setting.value;
                } else if (setting.key === 'OPENAI_API_KEY') {
                    newProviders.openai.key = setting.value;
                } else if (setting.key === 'GOOGLE_API_KEY') {
                    newProviders.google.key = setting.value;
                } else if (setting.key === 'GROQ_API_KEY') {
                    newProviders.groq.key = setting.value;
                } else if (setting.key === 'XAI_API_KEY') {
                    newProviders.xai.key = setting.value;
                } else if (setting.key === 'DEFAULT_LLM_PROVIDER') {
                    setDefaultProvider(setting.value);
                } else if (setting.key === 'DEFAULT_LLM_MODEL') {
                    setDefaultModel(setting.value);
                }
            });
            setProviders(newProviders);
        } catch (err) {
            console.error("Failed to load settings", err);
        }
    };

    const handleSave = async (e) => {
        e.preventDefault();
        if (!newKey || !newValue) return;
        setLoading(true);
        try {
            await saveSetting({
                key: newKey,
                value: newValue,
                category: newCategory
            });
            // Clear form
            setNewKey('');
            setNewValue('');
            await fetchSettings();
        } catch (err) {
            alert('Failed to save setting');
        } finally {
            setLoading(false);
        }
    };

    const updateExisting = async (key, val, cat) => {
        try {
            await saveSetting({ key, value: val, category: cat });
            fetchSettings();
        } catch (err) {
            alert('Failed to update');
        }
    };

    const saveProviderKey = async (provider, key) => {
        const keyName = `${provider.toUpperCase()}_API_KEY`;
        try {
            await saveSetting({
                key: keyName,
                value: key,
                category: 'llm_provider'
            });
            await fetchSettings();
            alert(`${provider} API key saved successfully!`);
        } catch (err) {
            alert('Failed to save API key');
        }
    };

    const saveDefaultProviderAndModel = async () => {
        try {
            await saveSetting({
                key: 'DEFAULT_LLM_PROVIDER',
                value: defaultProvider,
                category: 'llm_provider'
            });
            await saveSetting({
                key: 'DEFAULT_LLM_MODEL',
                value: defaultModel,
                category: 'llm_provider'
            });
            await fetchSettings();
            alert('Default LLM configuration saved!');
        } catch (err) {
            alert('Failed to save default configuration');
        }
    };

    const getProviderStatus = (provider) => {
        return providers[provider]?.key ? 'Configured' : 'Not Configured';
    };

    return (
        <div className="max-w-5xl mx-auto space-y-8">
            <header>
                <h1 className="text-2xl font-bold text-gray-900">System Configuration</h1>
                <p className="text-gray-500">Manage LLM providers, API keys, and system settings.</p>
            </header>

            {/* LLM Provider Configuration */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-xl font-semibold mb-4 text-gray-900">LLM Provider Configuration</h2>
                <p className="text-sm text-gray-600 mb-6">Configure your AI provider API keys and default settings for agents.</p>

                {/* Provider API Keys */}
                <div className="space-y-4 mb-6">
                    {Object.entries({
                        anthropic: 'Anthropic (Claude)',
                        openai: 'OpenAI (GPT)',
                        google: 'Google (Gemini)',
                        groq: 'Groq',
                        xai: 'xAI (Grok)'
                    }).map(([provider, label]) => (
                        <div key={provider} className="border rounded-lg p-4 hover:border-blue-300 transition">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-3">
                                    <h3 className="font-medium text-gray-900">{label}</h3>
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${
                                        getProviderStatus(provider) === 'Configured'
                                            ? 'bg-green-100 text-green-800'
                                            : 'bg-gray-100 text-gray-600'
                                    }`}>
                                        {getProviderStatus(provider)}
                                    </span>
                                </div>
                            </div>
                            <div className="flex gap-2">
                                <input
                                    type="password"
                                    value={providers[provider]?.key || ''}
                                    onChange={(e) => setProviders({
                                        ...providers,
                                        [provider]: { ...providers[provider], key: e.target.value }
                                    })}
                                    placeholder={`Enter ${label} API Key`}
                                    className="flex-1 p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none text-sm"
                                />
                                <button
                                    onClick={() => saveProviderKey(provider, providers[provider]?.key)}
                                    className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 text-sm"
                                >
                                    Save Key
                                </button>
                            </div>
                        </div>
                    ))}
                </div>

                {/* Default Provider & Model Selection */}
                <div className="border-t pt-6">
                    <h3 className="font-medium text-gray-900 mb-4">Default Configuration for New Agents</h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Default Provider</label>
                            <select
                                value={defaultProvider}
                                onChange={(e) => setDefaultProvider(e.target.value)}
                                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                <option value="anthropic">Anthropic (Claude)</option>
                                <option value="openai">OpenAI (GPT)</option>
                                <option value="google">Google (Gemini)</option>
                                <option value="groq">Groq</option>
                                <option value="xai">xAI (Grok)</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-2">Default Model</label>
                            <select
                                value={defaultModel}
                                onChange={(e) => setDefaultModel(e.target.value)}
                                className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                            >
                                {availableModels.map(model => (
                                    <option key={model} value={model}>{model}</option>
                                ))}
                            </select>
                        </div>
                    </div>
                    <button
                        onClick={saveDefaultProviderAndModel}
                        className="mt-4 bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
                    >
                        Save Default Configuration
                    </button>
                </div>
            </div>

            {/* Add New Setting */}
            <div className="bg-white p-6 rounded-lg shadow">
                <h2 className="text-lg font-medium mb-4">Add Custom Configuration</h2>
                <form onSubmit={handleSave} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Key</label>
                        <input
                            type="text"
                            value={newKey}
                            onChange={(e) => setNewKey(e.target.value)}
                            placeholder="e.g. ANTHROPIC_API_KEY"
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Value</label>
                        <input
                            type="text"
                            value={newValue}
                            onChange={(e) => setNewValue(e.target.value)}
                            placeholder="Value..."
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                            required
                        />
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Category</label>
                        <select
                            value={newCategory}
                            onChange={(e) => setNewCategory(e.target.value)}
                            className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500 outline-none"
                        >
                            <option value="general">General</option>
                            <option value="llm_provider">LLM Provider</option>
                            <option value="system">System</option>
                            <option value="notification">Notification</option>
                        </select>
                    </div>
                    <button
                        type="submit"
                        disabled={loading}
                        className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
                    >
                        {loading ? 'Saving...' : 'Save Config'}
                    </button>
                </form>
            </div>

            {/* Existing Settings List */}
            <div className="bg-white shadow overflow-hidden sm:rounded-lg">
                <div className="px-4 py-5 sm:px-6">
                    <h3 className="text-lg leading-6 font-medium text-gray-900">Current Configurations</h3>
                </div>
                <ul className="divide-y divide-gray-200">
                    {settings.map((setting) => (
                        <li key={setting.key} className="px-4 py-4 sm:px-6 flex items-center justify-between">
                            <div className="flex-1 min-w-0 grid grid-cols-1 md:grid-cols-3 gap-4">
                                <div>
                                    <p className="text-sm font-bold text-blue-600 truncate">{setting.key}</p>
                                    <p className="text-xs text-gray-500">{setting.category}</p>
                                </div>
                                <div className="md:col-span-2">
                                    <input
                                        type="text"
                                        defaultValue={setting.value}
                                        onBlur={(e) => {
                                            if (e.target.value !== setting.value) {
                                                updateExisting(setting.key, e.target.value, setting.category);
                                            }
                                        }}
                                        className="w-full bg-gray-50 border-none rounded p-1 text-sm text-gray-800 focus:ring-2 focus:ring-blue-500 cursor-text"
                                    />
                                </div>
                            </div>
                        </li>
                    ))}
                    {settings.length === 0 && (
                        <li className="px-4 py-8 text-center text-gray-500">No configurations set.</li>
                    )}
                </ul>
            </div>
        </div>
    );
}

export default Settings;
