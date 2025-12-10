import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './Layout';
import Dashboard from './pages/Dashboard';
import Projects from './pages/Projects';
import Agents from './pages/Agents';
import Jobs from './pages/Jobs';
import Users from './pages/Users';
import Teams from './pages/Teams';
import Audit from './pages/Audit';
import Settings from './pages/Settings';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="projects" element={<Projects />} />
          <Route path="agents" element={<Agents />} />
          <Route path="jobs" element={<Jobs />} />
          <Route path="users" element={<Users />} />
          <Route path="teams" element={<Teams />} />
          <Route path="audit" element={<Audit />} />
          <Route path="settings" element={<Settings />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
