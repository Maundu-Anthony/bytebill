import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Input } from '../components/ui/Input';
import { Alert } from '../components/ui/Alert';
import api from '../api/axios';

const CaptivePortal = () => {
  const [loginMethod, setLoginMethod] = useState('voucher'); // 'voucher' or 'mpesa'
  const [formData, setFormData] = useState({
    voucherCode: '',
    phoneNumber: '',
    mpesaCode: ''
  });
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [plans, setPlans] = useState([]);

  useEffect(() => {
    // Get available plans for M-PESA payment
    fetchPlans();
  }, []);

  const fetchPlans = async () => {
    try {
      const response = await api.get('/plans');
      setPlans(response.data.plans || []);
    } catch (err) {
      console.error('Error fetching plans:', err);
    }
  };

  const handleVoucherLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await api.post('/auth/user-login', {
        voucher_code: formData.voucherCode,
        mac_address: 'auto-detect', // This would be detected by the captive portal
        ip_address: 'auto-detect'
      });

      if (response.data.success) {
        setMessage('Login successful! You are now connected to the internet.');
        // Redirect to a success page or close the portal
        setTimeout(() => {
          window.location.href = 'http://google.com';
        }, 2000);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleMpesaPayment = async (planId) => {
    if (!formData.phoneNumber) {
      setError('Please enter your phone number');
      return;
    }

    setLoading(true);
    setError('');
    setMessage('');

    try {
      const response = await api.post('/payments/initiate', {
        phone_number: formData.phoneNumber,
        plan_id: planId
      });

      if (response.data.success) {
        setMessage('Payment request sent to your phone. Please complete the M-PESA payment.');
        // Poll for payment status
        pollPaymentStatus(response.data.checkout_request_id);
      }
    } catch (err) {
      setError(err.response?.data?.error || 'Payment initiation failed');
    } finally {
      setLoading(false);
    }
  };

  const pollPaymentStatus = async (checkoutRequestId) => {
    // Poll every 5 seconds for payment status
    const interval = setInterval(async () => {
      try {
        const response = await api.get(`/payments/status/${checkoutRequestId}`);
        
        if (response.data.status === 'completed') {
          clearInterval(interval);
          setMessage('Payment successful! You are now connected to the internet.');
          setTimeout(() => {
            window.location.href = 'http://google.com';
          }, 2000);
        } else if (response.data.status === 'failed') {
          clearInterval(interval);
          setError('Payment failed. Please try again.');
        }
      } catch (err) {
        console.error('Error checking payment status:', err);
      }
    }, 5000);

    // Stop polling after 5 minutes
    setTimeout(() => {
      clearInterval(interval);
    }, 300000);
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center py-12 px-4">
      <div className="max-w-lg w-full space-y-8">
        <div className="text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Welcome to ByteBill
          </h1>
          <p className="text-lg text-gray-600">
            Connect to the internet with a voucher or M-PESA payment
          </p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Choose Login Method</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {(message || error) && (
                <Alert type={error ? 'error' : 'success'}>
                  {message || error}
                </Alert>
              )}

              {/* Login Method Selection */}
              <div className="flex space-x-4">
                <Button
                  variant={loginMethod === 'voucher' ? 'primary' : 'outline'}
                  onClick={() => setLoginMethod('voucher')}
                  className="flex-1"
                >
                  Voucher Code
                </Button>
                <Button
                  variant={loginMethod === 'mpesa' ? 'primary' : 'outline'}
                  onClick={() => setLoginMethod('mpesa')}
                  className="flex-1"
                >
                  M-PESA Payment
                </Button>
              </div>

              {/* Voucher Login */}
              {loginMethod === 'voucher' && (
                <form onSubmit={handleVoucherLogin} className="space-y-4">
                  <div>
                    <label htmlFor="voucherCode" className="block text-sm font-medium text-gray-700">
                      Voucher Code
                    </label>
                    <Input
                      id="voucherCode"
                      name="voucherCode"
                      type="text"
                      required
                      value={formData.voucherCode}
                      onChange={handleChange}
                      placeholder="Enter your voucher code"
                      className="mt-1"
                    />
                  </div>
                  
                  <Button
                    type="submit"
                    disabled={loading}
                    className="w-full"
                  >
                    {loading ? 'Connecting...' : 'Connect'}
                  </Button>
                </form>
              )}

              {/* M-PESA Payment */}
              {loginMethod === 'mpesa' && (
                <div className="space-y-4">
                  <div>
                    <label htmlFor="phoneNumber" className="block text-sm font-medium text-gray-700">
                      Phone Number
                    </label>
                    <Input
                      id="phoneNumber"
                      name="phoneNumber"
                      type="tel"
                      required
                      value={formData.phoneNumber}
                      onChange={handleChange}
                      placeholder="0712345678"
                      className="mt-1"
                    />
                  </div>

                  <div className="space-y-3">
                    <h3 className="text-lg font-medium text-gray-900">Select a Plan</h3>
                    {plans.map((plan) => (
                      <div
                        key={plan.id}
                        className="border rounded-lg p-4 hover:bg-gray-50 cursor-pointer"
                        onClick={() => handleMpesaPayment(plan.id)}
                      >
                        <div className="flex justify-between items-center">
                          <div>
                            <h4 className="font-medium text-gray-900">{plan.name}</h4>
                            <p className="text-sm text-gray-600">{plan.description}</p>
                          </div>
                          <div className="text-right">
                            <p className="text-lg font-bold text-green-600">
                              KSh {plan.price}
                            </p>
                            <p className="text-xs text-gray-500">
                              {plan.duration_hours}h / {plan.data_limit_gb}GB
                            </p>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        <div className="text-center text-sm text-gray-500">
          <p>Need help? Contact support at support@bytebill.local</p>
        </div>
      </div>
    </div>
  );
};

export default CaptivePortal;
