import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Alert } from '../components/ui/Alert';
import api from '../api/axios';

const ISPMonitoring = () => {
  const [ispStatus, setIspStatus] = useState({});
  const [speedTest, setSpeedTest] = useState({});
  const [loading, setLoading] = useState(true);
  const [testingSpeed, setTestingSpeed] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchISPStatus();
  }, []);

  const fetchISPStatus = async () => {
    try {
      const response = await api.get('/api/isp/status');
      setIspStatus(response.data);
      setError('');
    } catch (err) {
      setError('Failed to fetch ISP status');
    } finally {
      setLoading(false);
    }
  };

  const runSpeedTest = async () => {
    setTestingSpeed(true);
    try {
      const response = await api.post('/api/isp/speedtest');
      setSpeedTest(response.data);
      setError('');
    } catch (err) {
      setError('Failed to run speed test');
    } finally {
      setTestingSpeed(false);
    }
  };

  const switchISP = async (ispId) => {
    try {
      await api.post(`/api/isp/switch/${ispId}`);
      fetchISPStatus();
    } catch (err) {
      setError('Failed to switch ISP');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading ISP status...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">ISP Monitoring</h1>
        <div className="space-x-2">
          <Button onClick={runSpeedTest} disabled={testingSpeed}>
            {testingSpeed ? 'Testing...' : 'Run Speed Test'}
          </Button>
          <Button onClick={fetchISPStatus}>Refresh</Button>
        </div>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      {/* Current ISP Status */}
      <Card>
        <CardHeader>
          <CardTitle>Current ISP Status</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="bg-blue-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Active ISP</h3>
              <p className="text-lg font-semibold text-blue-600">{ispStatus.active_isp || 'N/A'}</p>
            </div>
            <div className="bg-green-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Connection Status</h3>
              <p className={`text-lg font-semibold ${ispStatus.status === 'connected' ? 'text-green-600' : 'text-red-600'}`}>
                {ispStatus.status === 'connected' ? 'Connected' : 'Disconnected'}
              </p>
            </div>
            <div className="bg-yellow-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Latency</h3>
              <p className="text-lg font-semibold text-yellow-600">{ispStatus.latency || 'N/A'} ms</p>
            </div>
            <div className="bg-purple-50 p-4 rounded-lg">
              <h3 className="text-sm font-medium text-gray-500">Uptime</h3>
              <p className="text-lg font-semibold text-purple-600">{ispStatus.uptime || 'N/A'}</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Speed Test Results */}
      {speedTest.download && (
        <Card>
          <CardHeader>
            <CardTitle>Latest Speed Test Results</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center">
                <h3 className="text-sm font-medium text-gray-500">Download Speed</h3>
                <p className="text-2xl font-bold text-blue-600">{speedTest.download} Mbps</p>
              </div>
              <div className="text-center">
                <h3 className="text-sm font-medium text-gray-500">Upload Speed</h3>
                <p className="text-2xl font-bold text-green-600">{speedTest.upload} Mbps</p>
              </div>
              <div className="text-center">
                <h3 className="text-sm font-medium text-gray-500">Ping</h3>
                <p className="text-2xl font-bold text-yellow-600">{speedTest.ping} ms</p>
              </div>
            </div>
            <div className="mt-4 text-center text-sm text-gray-500">
              Last test: {new Date(speedTest.timestamp).toLocaleString()}
            </div>
          </CardContent>
        </Card>
      )}

      {/* ISP Management */}
      <Card>
        <CardHeader>
          <CardTitle>ISP Connections</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {ispStatus.isps && ispStatus.isps.map((isp) => (
              <div key={isp.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-4">
                  <div className={`w-3 h-3 rounded-full ${isp.status === 'active' ? 'bg-green-500' : 'bg-gray-300'}`}></div>
                  <div>
                    <h3 className="font-medium">{isp.name}</h3>
                    <p className="text-sm text-gray-500">{isp.interface}</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <div className="text-right">
                    <p className="text-sm font-medium">{isp.speed || 'Unknown'}</p>
                    <p className="text-xs text-gray-500">Max Speed</p>
                  </div>
                  {isp.status !== 'active' && (
                    <Button 
                      size="sm"
                      onClick={() => switchISP(isp.id)}
                    >
                      Switch to {isp.name}
                    </Button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Traffic Statistics */}
      <Card>
        <CardHeader>
          <CardTitle>Traffic Statistics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500">Data In (Today)</h3>
              <p className="text-lg font-semibold text-blue-600">{ispStatus.data_in || '0'} GB</p>
            </div>
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500">Data Out (Today)</h3>
              <p className="text-lg font-semibold text-green-600">{ispStatus.data_out || '0'} GB</p>
            </div>
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500">Peak Usage</h3>
              <p className="text-lg font-semibold text-yellow-600">{ispStatus.peak_usage || '0'} Mbps</p>
            </div>
            <div className="text-center">
              <h3 className="text-sm font-medium text-gray-500">Efficiency</h3>
              <p className="text-lg font-semibold text-purple-600">{ispStatus.efficiency || '0'}%</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ISPMonitoring;
