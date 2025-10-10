/**
 * API Status Page
 * 
 * This page displays the status of the FastAPI backend and provides
 * debugging information for development and deployment verification.
 */

import React, { useState, useEffect } from 'react';
import MainLayout from '@/components/Layout/MainLayout';
import { apiClient } from '@/services/api';

interface HealthStatus {
  status: string;
  timestamp: number;
  services: Record<string, string>;
  version: string;
}

interface ApiStatusInfo {
  isOnline: boolean;
  health?: HealthStatus;
  responseTime?: number;
  error?: string;
  lastChecked: Date;
}

/**
 * API Status Page Component
 * 
 * Features:
 * - Real-time backend health monitoring
 * - Service status breakdown
 * - Response time measurement
 * - Connection debugging information
 */
export default function ApiStatusPage() {
  const [apiStatus, setApiStatus] = useState<ApiStatusInfo>({
    isOnline: false,
    lastChecked: new Date(),
  });
  const [isLoading, setIsLoading] = useState(true);
  const [autoRefresh, setAutoRefresh] = useState(false);

  /**
   * Check API health and measure response time
   */
  const checkApiHealth = async () => {
    const startTime = Date.now();
    
    try {
      const response = await apiClient.checkApiHealth();
      const responseTime = Date.now() - startTime;
      
      setApiStatus({
        isOnline: true,
        health: response.data,
        responseTime,
        lastChecked: new Date(),
      });
    } catch (error) {
      const responseTime = Date.now() - startTime;
      
      setApiStatus({
        isOnline: false,
        responseTime,
        error: error instanceof Error ? error.message : 'Unknown error',
        lastChecked: new Date(),
      });
    } finally {
      setIsLoading(false);
    }
  };

  /**
   * Auto-refresh effect
   */
  useEffect(() => {
    checkApiHealth();
    
    let interval: NodeJS.Timeout;
    if (autoRefresh) {
      interval = setInterval(checkApiHealth, 5000); // Refresh every 5 seconds
    }
    
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh]);

  /**
   * Get status color based on service health
   */
  const getStatusColor = (status: string) => {
    switch (status.toLowerCase()) {
      case 'healthy':
        return 'text-green-400';
      case 'degraded':
        return 'text-yellow-400';
      case 'unhealthy':
        return 'text-red-400';
      default:
        return 'text-gray-400';
    }
  };

  /**
   * Format timestamp for display
   */
  const formatTimestamp = (timestamp: number) => {
    return new Date(timestamp * 1000).toLocaleString();
  };

  return (
    <MainLayout
      title="API Status - Steam Game Search Engine"
      description="Real-time status monitoring for the FastAPI backend services"
    >
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-white mb-4">
            FastAPI Backend Status
          </h1>
          <p className="text-gray-300">
            Real-time monitoring of the Python FastAPI backend services and health status.
          </p>
        </div>

        {/* Controls */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <button
              onClick={checkApiHealth}
              disabled={isLoading}
              className="btn-steam"
            >
              {isLoading ? 'Checking...' : 'Refresh Status'}
            </button>
            
            <label className="flex items-center space-x-2 text-gray-300">
              <input
                type="checkbox"
                checked={autoRefresh}
                onChange={(e) => setAutoRefresh(e.target.checked)}
                className="rounded border-gray-600 bg-steam-blue-dark text-steam-green focus:ring-steam-green"
              />
              <span>Auto-refresh (5s)</span>
            </label>
          </div>
          
          <div className="text-sm text-gray-400">
            Last checked: {apiStatus.lastChecked.toLocaleTimeString()}
          </div>
        </div>

        {/* Overall Status */}
        <div className="card-steam p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-white">Overall Status</h2>
            <div className={`flex items-center space-x-2 ${apiStatus.isOnline ? 'text-green-400' : 'text-red-400'}`}>
              <div className={`w-3 h-3 rounded-full ${apiStatus.isOnline ? 'bg-green-400' : 'bg-red-400'}`}></div>
              <span className="font-medium">
                {apiStatus.isOnline ? 'Online' : 'Offline'}
              </span>
            </div>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-steam-blue-light p-4 rounded">
              <div className="text-sm text-gray-300">Response Time</div>
              <div className="text-lg font-semibold text-white">
                {apiStatus.responseTime ? `${apiStatus.responseTime}ms` : 'N/A'}
              </div>
            </div>
            
            <div className="bg-steam-blue-light p-4 rounded">
              <div className="text-sm text-gray-300">API Version</div>
              <div className="text-lg font-semibold text-white">
                {apiStatus.health?.version || 'Unknown'}
              </div>
            </div>
            
            <div className="bg-steam-blue-light p-4 rounded">
              <div className="text-sm text-gray-300">Backend URL</div>
              <div className="text-lg font-semibold text-white break-all">
                {process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000'}
              </div>
            </div>
          </div>
        </div>

        {/* Service Status */}
        {apiStatus.health && (
          <div className="card-steam p-6 mb-6">
            <h2 className="text-xl font-semibold text-white mb-4">Service Status</h2>
            
            <div className="space-y-3">
              {Object.entries(apiStatus.health.services).map(([service, status]) => (
                <div key={service} className="flex items-center justify-between p-3 bg-steam-blue-light rounded">
                  <div className="flex items-center space-x-3">
                    <div className={`w-2 h-2 rounded-full ${
                      status === 'healthy' ? 'bg-green-400' : 
                      status === 'degraded' ? 'bg-yellow-400' : 'bg-red-400'
                    }`}></div>
                    <span className="text-white font-medium capitalize">
                      {service.replace('_', ' ')}
                    </span>
                  </div>
                  <span className={`font-medium capitalize ${getStatusColor(status)}`}>
                    {status}
                  </span>
                </div>
              ))}
            </div>
            
            <div className="mt-4 text-sm text-gray-400">
              Health check timestamp: {formatTimestamp(apiStatus.health.timestamp)}
            </div>
          </div>
        )}

        {/* Error Information */}
        {apiStatus.error && (
          <div className="card-steam p-6 mb-6 border-l-4 border-red-400">
            <h2 className="text-xl font-semibold text-red-400 mb-4">Connection Error</h2>
            <div className="bg-red-900/20 p-4 rounded">
              <pre className="text-red-300 text-sm whitespace-pre-wrap">
                {apiStatus.error}
              </pre>
            </div>
            
            <div className="mt-4 text-sm text-gray-400">
              <h3 className="font-medium text-white mb-2">Troubleshooting Steps:</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>Verify the FastAPI backend is running on the configured port</li>
                <li>Check if the API_BASE_URL environment variable is correct</li>
                <li>Ensure CORS is properly configured in the backend</li>
                <li>Check network connectivity and firewall settings</li>
              </ul>
            </div>
          </div>
        )}

        {/* Configuration Information */}
        <div className="card-steam p-6">
          <h2 className="text-xl font-semibold text-white mb-4">Configuration</h2>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <h3 className="font-medium text-white mb-2">Environment Variables</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-gray-300">API Base URL:</span>
                  <span className="text-white font-mono">
                    {process.env.NEXT_PUBLIC_API_BASE_URL || 'Not set'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">App URL:</span>
                  <span className="text-white font-mono">
                    {process.env.NEXT_PUBLIC_APP_URL || 'Not set'}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-300">Debug Mode:</span>
                  <span className="text-white font-mono">
                    {process.env.NEXT_PUBLIC_DEBUG || 'false'}
                  </span>
                </div>
              </div>
            </div>
            
            <div>
              <h3 className="font-medium text-white mb-2">API Endpoints</h3>
              <div className="space-y-2 text-sm">
                <div className="text-gray-300">
                  <div>• POST /api/v1/search/games</div>
                  <div>• GET /api/v1/search/suggest</div>
                  <div>• GET /api/v1/games/{'{id}'}</div>
                  <div>• GET /api/v1/health</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </MainLayout>
  );
}
