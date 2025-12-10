import React, { useState, useEffect } from 'react';
import { getAllJobs } from '../api';

function Jobs() {
    const [jobs, setJobs] = useState([]);

    useEffect(() => {
        fetchJobs();
        const interval = setInterval(fetchJobs, 3000);
        return () => clearInterval(interval);
    }, []);

    const fetchJobs = async () => {
        const res = await getAllJobs();
        setJobs(res.data);
    };

    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-2xl font-bold text-gray-900">All Jobs</h1>
                <span className="bg-gray-100 text-gray-800 text-xs font-semibold px-2.5 py-0.5 rounded">
                    {jobs.length} Total
                </span>
            </div>

            <div className="bg-white shadow overflow-hidden sm:rounded-md">
                <ul className="divide-y divide-gray-200">
                    {jobs.map((job) => (
                        <li key={job.id}>
                            <div className="px-4 py-4 sm:px-6">
                                <div className="flex items-center justify-between">
                                    <p className="text-sm font-medium text-blue-600 truncate">
                                        Job #{job.id} - {job.type}
                                    </p>
                                    <div className="ml-2 flex-shrink-0 flex">
                                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${job.status === 'completed' ? 'bg-green-100 text-green-800' :
                                                job.status === 'failed' ? 'bg-red-100 text-red-800' :
                                                    job.status === 'running' ? 'bg-blue-100 text-blue-800' :
                                                        'bg-gray-100 text-gray-800'
                                            }`}>
                                            {job.status}
                                        </span>
                                    </div>
                                </div>
                                <div className="mt-2 sm:flex sm:justify-between">
                                    <div className="sm:flex">
                                        <p className="flex items-center text-sm text-gray-500 font-mono">
                                            {job.payload?.task}
                                        </p>
                                    </div>
                                    <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                                        <p>
                                            Project {job.project_id} • {new Date(job.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                </div>
                                {(job.result || job.logs) && (
                                    <div className="mt-2 bg-gray-50 p-2 rounded text-xs font-mono overflow-auto max-h-40">
                                        {JSON.stringify(job.result || job.logs, null, 2)}
                                    </div>
                                )}
                            </div>
                        </li>
                    ))}
                    {jobs.length === 0 && (
                        <li className="px-4 py-8 text-center text-gray-500">
                            No jobs found found. Go to Projects to start a mission.
                        </li>
                    )}
                </ul>
            </div>
        </div>
    );
}

export default Jobs;
