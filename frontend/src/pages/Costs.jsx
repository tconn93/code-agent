import { useState, useEffect } from 'react';
import api from '../api';

export default function Costs() {
  const [projects, setProjects] = useState([]);
  const [selectedProject, setSelectedProject] = useState(null);
  const [projectCost, setProjectCost] = useState(null);
  const [budgetStatus, setBudgetStatus] = useState(null);
  const [periodDays, setPeriodDays] = useState(30);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  useEffect(() => {
    if (selectedProject) {
      loadProjectCosts();
      loadBudgetStatus();
    }
  }, [selectedProject, periodDays]);

  const loadProjects = async () => {
    try {
      const response = await api.get('/projects/');
      setProjects(response.data);
      if (response.data.length > 0) {
        setSelectedProject(response.data[0].id);
      }
    } catch (err) {
      console.error('Error loading projects:', err);
    }
  };

  const loadProjectCosts = async () => {
    if (!selectedProject) return;
    setLoading(true);

    try {
      const response = await api.get(`/costs/projects/${selectedProject}`, {
        params: { period_days: periodDays }
      });
      setProjectCost(response.data);
    } catch (err) {
      console.error('Error loading project costs:', err);
    } finally {
      setLoading(false);
    }
  };

  const loadBudgetStatus = async () => {
    if (!selectedProject) return;

    try {
      const response = await api.get(`/costs/projects/${selectedProject}/budget`);
      setBudgetStatus(response.data);
    } catch (err) {
      console.error('Error loading budget status:', err);
    }
  };

  const getBudgetStatusColor = (status) => {
    switch (status) {
      case 'ok':
        return 'bg-green-100 text-green-800';
      case 'warning':
        return 'bg-yellow-100 text-yellow-800';
      case 'critical':
        return 'bg-orange-100 text-orange-800';
      case 'exceeded':
        return 'bg-red-100 text-red-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount || 0);
  };

  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-6">Cost Tracking & Budget Management</h1>

      {/* Project Selector */}
      <div className="mb-6 flex gap-4 items-center">
        <div className="flex-1">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Select Project
          </label>
          <select
            value={selectedProject || ''}
            onChange={(e) => setSelectedProject(Number(e.target.value))}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value="">Choose a project</option>
            {projects.map((project) => (
              <option key={project.id} value={project.id}>
                {project.name}
              </option>
            ))}
          </select>
        </div>

        <div className="w-48">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Period
          </label>
          <select
            value={periodDays}
            onChange={(e) => setPeriodDays(Number(e.target.value))}
            className="w-full border border-gray-300 rounded-md px-3 py-2"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
            <option value={null}>All time</option>
          </select>
        </div>
      </div>

      {/* Budget Status Card */}
      {budgetStatus && budgetStatus.has_budget && (
        <div className="mb-6 bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">Budget Status</h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Budget Allocated</p>
              <p className="text-2xl font-bold">{formatCurrency(budgetStatus.budget_allocated)}</p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Actual Cost</p>
              <p className="text-2xl font-bold">{formatCurrency(budgetStatus.actual_cost)}</p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Remaining Budget</p>
              <p className={`text-2xl font-bold ${budgetStatus.remaining_budget < 0 ? 'text-red-600' : 'text-green-600'}`}>
                {formatCurrency(budgetStatus.remaining_budget)}
              </p>
            </div>

            <div>
              <p className="text-sm text-gray-600 mb-2">Status</p>
              <span className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${getBudgetStatusColor(budgetStatus.status)}`}>
                {budgetStatus.status.toUpperCase()} ({budgetStatus.percentage_used.toFixed(1)}%)
              </span>
            </div>
          </div>

          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-4">
              <div
                className={`h-4 rounded-full transition-all ${
                  budgetStatus.status === 'exceeded' ? 'bg-red-600' :
                  budgetStatus.status === 'critical' ? 'bg-orange-600' :
                  budgetStatus.status === 'warning' ? 'bg-yellow-600' :
                  'bg-green-600'
                }`}
                style={{ width: `${Math.min(budgetStatus.percentage_used, 100)}%` }}
              ></div>
            </div>
          </div>

          {/* Warnings */}
          {budgetStatus.status === 'exceeded' && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-md p-4">
              <p className="text-red-800 font-medium">
                ⚠️ Budget Exceeded! New jobs will be blocked until budget is increased.
              </p>
            </div>
          )}
          {budgetStatus.status === 'critical' && (
            <div className="mt-4 bg-orange-50 border border-orange-200 rounded-md p-4">
              <p className="text-orange-800 font-medium">
                ⚠️ Budget Critical! You're at {budgetStatus.percentage_used.toFixed(1)}% of allocated budget.
              </p>
            </div>
          )}
          {budgetStatus.status === 'warning' && (
            <div className="mt-4 bg-yellow-50 border border-yellow-200 rounded-md p-4">
              <p className="text-yellow-800 font-medium">
                ⚠️ Budget Warning! You've used {budgetStatus.percentage_used.toFixed(1)}% of allocated budget.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Cost Summary Card */}
      {projectCost && (
        <div className="bg-white border border-gray-200 rounded-lg shadow-sm p-6">
          <h2 className="text-lg font-semibold mb-4">
            Cost Summary - {periodDays ? `Last ${periodDays} days` : 'All Time'}
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="border-r border-gray-200 pr-4">
              <p className="text-sm text-gray-600">Total Cost</p>
              <p className="text-3xl font-bold text-blue-600">{formatCurrency(projectCost.total_cost)}</p>
            </div>

            <div className="border-r border-gray-200 pr-4">
              <p className="text-sm text-gray-600">Total Jobs</p>
              <p className="text-2xl font-semibold">{projectCost.total_jobs}</p>
            </div>

            <div className="border-r border-gray-200 pr-4">
              <p className="text-sm text-gray-600">Completed Jobs</p>
              <p className="text-2xl font-semibold text-green-600">{projectCost.completed_jobs}</p>
            </div>

            <div>
              <p className="text-sm text-gray-600">Failed Jobs</p>
              <p className="text-2xl font-semibold text-red-600">{projectCost.failed_jobs}</p>
            </div>
          </div>

          <div className="mt-6 pt-4 border-t border-gray-200">
            <p className="text-sm text-gray-600">Average Cost per Job</p>
            <p className="text-xl font-semibold">{formatCurrency(projectCost.average_cost_per_job)}</p>
          </div>

          {loading && (
            <div className="mt-4 text-center text-gray-500">
              <p>Loading...</p>
            </div>
          )}
        </div>
      )}

      {!selectedProject && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <p className="text-gray-600">Select a project to view cost tracking and budget information.</p>
        </div>
      )}
    </div>
  );
}
