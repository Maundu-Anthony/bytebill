import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Alert } from '../components/ui/Alert';
import api from '../api/axios';

const Settings = () => {
  const [settings, setSettings] = useState({
    system: {
      company_name: '',
      logo_url: '',
      currency: 'KSh',
      timezone: 'Africa/Nairobi'
    },
    network: {
      hotspot_name: '',
      gateway_ip: '',
      dns_primary: '8.8.8.8',
      dns_secondary: '8.8.4.4',
      bandwidth_limit: 10,
      session_timeout: 3600
    },
    payment: {
      mpesa_business_shortcode: '',
      mpesa_consumer_key: '',
      mpesa_consumer_secret: '',
      mpesa_passkey: ''
    },
    captive_portal: {
      welcome_message: 'Welcome to our WiFi hotspot',
      terms_url: '',
      support_phone: '',
      support_email: ''
    }
  });
  
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [activeTab, setActiveTab] = useState('system');

  useEffect(() => {
    fetchSettings();
  }, []);

  const fetchSettings = async () => {
    try {
      const response = await api.get('/api/settings');
      setSettings(response.data.settings);
      setError('');
    } catch (err) {
      setError('Failed to fetch settings');
    } finally {
      setLoading(false);
    }
  };

  const saveSettings = async () => {
    setSaving(true);
    setError('');
    setSuccess('');
    
    try {
      await api.post('/api/settings', settings);
      setSuccess('Settings saved successfully');
    } catch (err) {
      setError('Failed to save settings');
    } finally {
      setSaving(false);
    }
  };

  const updateSetting = (category, key, value) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value
      }
    }));
  };

  const tabs = [
    { id: 'system', label: 'System' },
    { id: 'network', label: 'Network' },
    { id: 'payment', label: 'Payment' },
    { id: 'captive_portal', label: 'Captive Portal' }
  ];

  if (loading) {
    return <div className="flex items-center justify-center h-64">Loading settings...</div>;
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Settings</h1>
        <Button onClick={saveSettings} disabled={saving}>
          {saving ? 'Saving...' : 'Save Settings'}
        </Button>
      </div>

      {error && <Alert type="error">{error}</Alert>}
      {success && <Alert type="success">{success}</Alert>}

      {/* Settings Tabs */}
      <Card>
        <CardHeader>
          <div className="flex space-x-1 border-b">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`px-4 py-2 text-sm font-medium rounded-t-lg ${
                  activeTab === tab.id
                    ? 'bg-blue-100 text-blue-700 border-b-2 border-blue-700'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </CardHeader>
        <CardContent>
          {/* System Settings */}
          {activeTab === 'system' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">System Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Company Name</label>
                  <Input
                    value={settings.system.company_name}
                    onChange={(e) => updateSetting('system', 'company_name', e.target.value)}
                    placeholder="Your Company Name"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Logo URL</label>
                  <Input
                    value={settings.system.logo_url}
                    onChange={(e) => updateSetting('system', 'logo_url', e.target.value)}
                    placeholder="https://example.com/logo.png"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Currency</label>
                  <select
                    value={settings.system.currency}
                    onChange={(e) => updateSetting('system', 'currency', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="KSh">KSh (Kenyan Shilling)</option>
                    <option value="USD">USD (US Dollar)</option>
                    <option value="EUR">EUR (Euro)</option>
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Timezone</label>
                  <select
                    value={settings.system.timezone}
                    onChange={(e) => updateSetting('system', 'timezone', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="Africa/Nairobi">Africa/Nairobi</option>
                    <option value="UTC">UTC</option>
                    <option value="America/New_York">America/New_York</option>
                  </select>
                </div>
              </div>
            </div>
          )}

          {/* Network Settings */}
          {activeTab === 'network' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Network Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Hotspot Name (SSID)</label>
                  <Input
                    value={settings.network.hotspot_name}
                    onChange={(e) => updateSetting('network', 'hotspot_name', e.target.value)}
                    placeholder="MyHotspot"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Gateway IP</label>
                  <Input
                    value={settings.network.gateway_ip}
                    onChange={(e) => updateSetting('network', 'gateway_ip', e.target.value)}
                    placeholder="192.168.1.1"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Primary DNS</label>
                  <Input
                    value={settings.network.dns_primary}
                    onChange={(e) => updateSetting('network', 'dns_primary', e.target.value)}
                    placeholder="8.8.8.8"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Secondary DNS</label>
                  <Input
                    value={settings.network.dns_secondary}
                    onChange={(e) => updateSetting('network', 'dns_secondary', e.target.value)}
                    placeholder="8.8.4.4"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Bandwidth Limit (Mbps)</label>
                  <Input
                    type="number"
                    value={settings.network.bandwidth_limit}
                    onChange={(e) => updateSetting('network', 'bandwidth_limit', parseInt(e.target.value))}
                    placeholder="10"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (seconds)</label>
                  <Input
                    type="number"
                    value={settings.network.session_timeout}
                    onChange={(e) => updateSetting('network', 'session_timeout', parseInt(e.target.value))}
                    placeholder="3600"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Payment Settings */}
          {activeTab === 'payment' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">M-PESA Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Business Short Code</label>
                  <Input
                    value={settings.payment.mpesa_business_shortcode}
                    onChange={(e) => updateSetting('payment', 'mpesa_business_shortcode', e.target.value)}
                    placeholder="174379"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Consumer Key</label>
                  <Input
                    value={settings.payment.mpesa_consumer_key}
                    onChange={(e) => updateSetting('payment', 'mpesa_consumer_key', e.target.value)}
                    placeholder="Your Consumer Key"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Consumer Secret</label>
                  <Input
                    type="password"
                    value={settings.payment.mpesa_consumer_secret}
                    onChange={(e) => updateSetting('payment', 'mpesa_consumer_secret', e.target.value)}
                    placeholder="Your Consumer Secret"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Passkey</label>
                  <Input
                    type="password"
                    value={settings.payment.mpesa_passkey}
                    onChange={(e) => updateSetting('payment', 'mpesa_passkey', e.target.value)}
                    placeholder="Your Passkey"
                  />
                </div>
              </div>
            </div>
          )}

          {/* Captive Portal Settings */}
          {activeTab === 'captive_portal' && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium text-gray-900">Captive Portal Configuration</h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="md:col-span-2">
                  <label className="block text-sm font-medium text-gray-700 mb-2">Welcome Message</label>
                  <textarea
                    value={settings.captive_portal.welcome_message}
                    onChange={(e) => updateSetting('captive_portal', 'welcome_message', e.target.value)}
                    rows="3"
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Welcome to our WiFi hotspot"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Terms & Conditions URL</label>
                  <Input
                    value={settings.captive_portal.terms_url}
                    onChange={(e) => updateSetting('captive_portal', 'terms_url', e.target.value)}
                    placeholder="https://example.com/terms"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Support Phone</label>
                  <Input
                    value={settings.captive_portal.support_phone}
                    onChange={(e) => updateSetting('captive_portal', 'support_phone', e.target.value)}
                    placeholder="+254700000000"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Support Email</label>
                  <Input
                    type="email"
                    value={settings.captive_portal.support_email}
                    onChange={(e) => updateSetting('captive_portal', 'support_email', e.target.value)}
                    placeholder="support@example.com"
                  />
                </div>
              </div>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex justify-end space-x-4">
        <Button variant="secondary" onClick={fetchSettings}>
          Reset Changes
        </Button>
        <Button onClick={saveSettings} disabled={saving}>
          {saving ? 'Saving...' : 'Save All Settings'}
        </Button>
      </div>
    </div>
  );
};

export default Settings;
