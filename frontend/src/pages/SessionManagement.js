import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import api from '../api/axios';

const SessionManagement = () => {
  const [sessions, setSessions] = useState([]);
  const [statistics, setStatistics] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filter, setFilter] = useState('all'); // all, active, expired

  useEffect(() => {
    fetchSessions();
    fetchStatistics();
  }, [filter]); // eslint-disable-line react-hooks/exhaustive-deps

  const fetchSessions = async () => {
    try {
      const response = await api.get(`/api/sessions?filter=${filter}`);
      setSessions(response.data.sessions || []);
      setError('');
    } catch (err) {
      setError('Failed to fetch sessions');
    } finally {
      setLoading(false);
    }
  };

  const fetchStatistics = async () => {
    try {
      const response = await api.get('/api/sessions/statistics');
      setStatistics(response.data);
    } catch (err) {
      console.error('Failed to fetch statistics');
    }
  };

  const terminateSession = async (sessionId) => {
    try {
      await api.post(`/api/sessions/${sessionId}/terminate`);
      fetchSessions();
      fetchStatistics();
    } catch (err) {
      setError('Failed to terminate session');
    }
  };

  const extendSession = async (sessionId, minutes) => {
    try {
      await api.post(`/api/sessions/${sessionId}/extend`, { minutes });
      fetchSessions();
    } catch (err) {
      setError('Failed to extend session');
    }
  };

  const formatDuration = (minutes) => {
    const hours = Math.floor(minutes / 60);
    const mins = minutes % 60;
    return hours > 0 ? `${hours}h ${mins}m` : `${mins}m`;
  };

  const formatDataSize = (bytes) => {
    if (bytes < 1024 * 1024) {
      return `${(bytes / 1024).toFixed(1)} KB`;
    } else if (bytes < 1024 * 1024 * 1024) {
      return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
    } else {
      return `${(bytes / (1024 * 1024 * 1024)).toFixed(2)} GB`;
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading sessions...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Session Management</h1>
        <Button onClick={() => { fetchSessions(); fetchStatistics(); }}>Refresh</Button>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      {/* Session Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500">Active Sessions</h3>
              <p className="text-2xl font-bold text-green-600">{statistics.active || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500">Total Sessions Today</h3>
              <p className="text-2xl font-bold text-blue-600">{statistics.today || 0}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500">Data Used Today</h3>
              <p className="text-2xl font-bold text-purple-600">{formatDataSize(statistics.data_today || 0)}</p>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-6">
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500">Revenue Today</h3>
              <p className="text-2xl font-bold text-yellow-600">KSh {statistics.revenue_today || 0}</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Session Filters */}
      <Card>
        <CardHeader>
          <CardTitle>Session Filters</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex space-x-2">
            {['all', 'active', 'expired'].map((filterType) => (
              <Button
                key={filterType}
                variant={filter === filterType ? 'primary' : 'secondary'}
                onClick={() => setFilter(filterType)}
              >
                {filterType.charAt(0).toUpperCase() + filterType.slice(1)} Sessions
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Sessions Table */}
      <Card>
        <CardHeader>
          <CardTitle>Session Details</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">User</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Start Time</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Duration</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data Used</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {sessions.map((session) => (
                  <tr key={session.id}>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div>
                        <div className="text-sm font-medium text-gray-900">{session.device_name || 'Unknown Device'}</div>
                        <div className="text-sm text-gray-500">{session.ip_address}</div>
                        <div className="text-xs text-gray-400 font-mono">{session.mac_address}</div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="text-sm text-gray-900">{session.plan_name}</div>
                      <div className="text-xs text-gray-500">KSh {session.plan_price}</div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(session.start_time).toLocaleString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDuration(session.duration_minutes)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatDataSize(session.data_used)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        session.status === 'active' ? 'bg-green-100 text-green-800' :
                        session.status === 'expired' ? 'bg-red-100 text-red-800' :
                        'bg-gray-100 text-gray-800'
                      }`}>
                        {session.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium space-x-2">
                      {session.status === 'active' && (
                        <>
                          <Button
                            size="sm"
                            variant="secondary"
                            onClick={() => extendSession(session.id, 30)}
                          >
                            +30m
                          </Button>
                          <Button
                            size="sm"
                            variant="danger"
                            onClick={() => terminateSession(session.id)}
                          >
                            Terminate
                          </Button>
                        </>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          {sessions.length === 0 && (
            <div className="text-center py-8 text-gray-500">
              No sessions found for the selected filter
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default SessionManagement;
