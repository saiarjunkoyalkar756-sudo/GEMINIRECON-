import React, { useEffect, useState } from 'react';

const VulnerabilityDashboard = () => {
  const [vulns, setVulns] = useState([]);

  // Assuming the FastAPI dashboard is running on port 8000/api
  // We'll update the API server to serve this JSON
  useEffect(() => {
    fetch('http://localhost:8000/api/vulnerabilities')
      .then(res => res.json())
      .then(data => setVulns(data))
      .catch(err => console.error("Error fetching vulns:", err));
  }, []);

  return (
    <div className="container mx-auto p-4 bg-gray-900 text-white min-h-screen">
      <h1 className="text-2xl font-bold mb-4 text-blue-500">GEMINIRECON Vulnerability Dashboard</h1>
      <table className="min-w-full bg-gray-800 rounded">
        <thead>
          <tr>
            <th className="py-2 px-4 border-b">Target</th>
            <th className="py-2 px-4 border-b">Severity</th>
            <th className="py-2 px-4 border-b">Template</th>
            <th className="py-2 px-4 border-b">URL</th>
          </tr>
        </thead>
        <tbody>
          {vulns.map((v, i) => (
            <tr key={i}>
              <td className="py-2 px-4 border-b">{v.target}</td>
              <td className={`py-2 px-4 border-b ${v.severity === 'high' ? 'text-red-500' : 'text-yellow-500'}`}>{v.severity}</td>
              <td className="py-2 px-4 border-b">{v.template}</td>
              <td className="py-2 px-4 border-b">{v.url}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default VulnerabilityDashboard;
