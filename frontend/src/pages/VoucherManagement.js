import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Alert } from '../components/ui/Alert';
import api from '../api/axios';

const VoucherManagement = () => {
  const [vouchers, setVouchers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showGenerateForm, setShowGenerateForm] = useState(false);
  const [generateForm, setGenerateForm] = useState({
    count: 10,
    plan: 'daily',
    expires_in_days: 7
  });

  useEffect(() => {
    fetchVouchers();
  }, []);

  const fetchVouchers = async () => {
    try {
      const response = await api.get('/api/vouchers');
      setVouchers(response.data.vouchers || []);
      setError('');
    } catch (err) {
      setError('Failed to fetch vouchers');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerate = async (e) => {
    e.preventDefault();
    try {
      await api.post('/api/vouchers/generate', generateForm);
      setShowGenerateForm(false);
      fetchVouchers();
    } catch (err) {
      setError('Failed to generate vouchers');
    }
  };

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading vouchers...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Voucher Management</h1>
        <Button onClick={() => setShowGenerateForm(true)}>
          Generate Vouchers
        </Button>
      </div>

      {error && <Alert type="error">{error}</Alert>}

      {showGenerateForm && (
        <Card>
          <CardHeader>
            <CardTitle>Generate New Vouchers</CardTitle>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleGenerate} className="space-y-4">
              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Count</label>
                  <Input
                    type="number"
                    value={generateForm.count}
                    onChange={(e) => setGenerateForm({...generateForm, count: parseInt(e.target.value)})}
                    min="1"
                    max="100"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Plan</label>
                  <select
                    value={generateForm.plan}
                    onChange={(e) => setGenerateForm({...generateForm, plan: e.target.value})}
                    className="block w-full px-3 py-2 border border-gray-300 rounded-md"
                  >
                    <option value="hourly">Hourly</option>
                    <option value="daily">Daily</option>
                    <option value="weekly">Weekly</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Expires in (days)</label>
                  <Input
                    type="number"
                    value={generateForm.expires_in_days}
                    onChange={(e) => setGenerateForm({...generateForm, expires_in_days: parseInt(e.target.value)})}
                    min="1"
                    max="365"
                  />
                </div>
              </div>
              <div className="flex space-x-4">
                <Button type="submit">Generate</Button>
                <Button variant="outline" onClick={() => setShowGenerateForm(false)}>Cancel</Button>
              </div>
            </form>
          </CardContent>
        </Card>
      )}

      <Card>
        <CardHeader>
          <CardTitle>Voucher List</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Code</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Plan</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Created</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Expires</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {vouchers.map((voucher) => (
                  <tr key={voucher.id}>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono">{voucher.code}</td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">{voucher.plan}</td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 py-1 text-xs rounded-full ${
                        voucher.status === 'unused' ? 'bg-green-100 text-green-800' :
                        voucher.status === 'used' ? 'bg-blue-100 text-blue-800' :
                        'bg-red-100 text-red-800'
                      }`}>
                        {voucher.status}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(voucher.created_at).toLocaleDateString()}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {new Date(voucher.expires_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default VoucherManagement;
