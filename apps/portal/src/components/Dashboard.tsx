"use client";
import React, { useState, useEffect } from 'react';
import { DashboardData, ScraperHealthStatus, RecentError, RevenueForecast } from './types';

// Heroicons as inline SVG components
const ChartBarIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
    </svg>
);

const UsersIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
    </svg>
);

const MailIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
    </svg>
);

const GlobeIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
    </svg>
);

const UserCircleIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5.121 17.804A13.937 13.937 0 0112 16c2.5 0 4.847.655 6.879 1.804M15 10a3 3 0 11-6 0 3 3 0 016 0zm6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const ServerIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
    </svg>
);

const ExclamationIcon = () => (
    <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
);

const ClockIcon = () => (
    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
    </svg>
);

const API_ENDPOINT = 'https://sovereign-empire-api-908fw2.abacusai.app/api/dashboard-stats';
const BEARER_TOKEN = 'Bearer sovereign_abacus_webhook_2026_xyz99';
const REFRESH_INTERVAL = 60000; // 60 seconds

const Dashboard: React.FC = () => {
    const [data, setData] = useState<DashboardData | null>(null);
    const [forecastData, setForecastData] = useState<RevenueForecast | null>(null);
    const [loading, setLoading] = useState<boolean>(true);
    const [error, setError] = useState<string | null>(null);
    const [lastUpdated, setLastUpdated] = useState<Date>(new Date());

    const fetchDashboardData = async () => {
        try {
            const [abacusRes, forecastRes] = await Promise.all([
                fetch(API_ENDPOINT, {
                    method: 'GET',
                    headers: {
                        'Authorization': BEARER_TOKEN,
                        'Content-Type': 'application/json',
                    },
                }),
                fetch('/api/revenue-forecast')
            ]);

            if (!abacusRes.ok) {
                throw new Error(`HTTP error! status: ${abacusRes.status}`);
            }

            const jsonData: DashboardData = await abacusRes.json();
            setData(jsonData);

            if (forecastRes.ok) {
                const fData: RevenueForecast = await forecastRes.json();
                setForecastData(fData);
            }

            setError(null);
            setLastUpdated(new Date());
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Failed to fetch dashboard data');
            console.error('Dashboard fetch error:', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchDashboardData();
        const interval = setInterval(fetchDashboardData, REFRESH_INTERVAL);
        return () => clearInterval(interval);
    }, []);

    const getHealthColor = (status: ScraperHealthStatus): string => {
        switch (status) {
            case 'healthy':
                return 'text-green-400 bg-green-500/20 border-green-500/50';
            case 'degraded':
                return 'text-yellow-400 bg-yellow-500/20 border-yellow-500/50';
            case 'critical':
                return 'text-red-400 bg-red-500/20 border-red-500/50';
            default:
                return 'text-gray-400 bg-gray-500/20 border-gray-500/50';
        }
    };

    const getHealthDotColor = (status: ScraperHealthStatus): string => {
        switch (status) {
            case 'healthy':
                return 'bg-green-500';
            case 'degraded':
                return 'bg-yellow-500';
            case 'critical':
                return 'bg-red-500';
            default:
                return 'bg-gray-500';
        }
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-purple-500 mb-4"></div>
                    <p className="text-gray-400 text-lg">Loading Dashboard...</p>
                </div>
            </div>
        );
    }

    if (error) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 flex items-center justify-center">
                <div className="bg-red-500/10 border border-red-500/50 rounded-lg p-8 max-w-md backdrop-blur-sm">
                    <div className="flex items-center gap-3 mb-4">
                        <ExclamationIcon />
                        <h2 className="text-red-400 text-xl font-semibold">Error Loading Dashboard</h2>
                    </div>
                    <p className="text-gray-300">{error}</p>
                    <button
                        onClick={() => {
                            setLoading(true);
                            fetchDashboardData();
                        }}
                        className="mt-6 px-6 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/50 rounded-lg text-red-400 transition-all duration-200"
                    >
                        Retry
                    </button>
                </div>
            </div>
        );
    }

    if (!data) return null;

    return (
        <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-900 to-gray-800 text-white p-6 md:p-8">
            <div className="max-w-7xl mx-auto">
                {/* Hero Section */}
                <div className="mb-8 text-center flex flex-col items-center">
                    <h1 className="text-4xl md:text-5xl font-bold mb-3 bg-gradient-to-r from-purple-400 via-blue-400 to-cyan-400 bg-clip-text text-transparent animate-gradient">
                        Sovereign Empire Command Center
                    </h1>
                    <p className="text-gray-400 text-lg">Real-time Business Intelligence & API Monitoring</p>
                    <div className="flex flex-col md:flex-row items-center justify-center gap-4 mt-6">
                        <div className="flex items-center gap-2 text-sm text-gray-500">
                            <ClockIcon />
                            <span>Last updated: {lastUpdated.toLocaleString()}</span>
                        </div>
                        <a href="/dashboard/seo-audit" className="px-5 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/50 text-indigo-400 hover:bg-indigo-500/20 hover:text-indigo-300 transition-all text-sm font-semibold flex items-center gap-2">
                            <GlobeIcon />
                            Abacus SEO Audit Deck
                        </a>
                    </div>
                </div>

                {/* Executive Metrics */}
                <div className="mb-8">
                    <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                        <ChartBarIcon />
                        Executive Overview
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="group bg-gradient-to-br from-gray-800/50 to-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6 hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-purple-500/20 rounded-lg group-hover:bg-purple-500/30 transition-colors">
                                    <UsersIcon />
                                </div>
                                <span className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-purple-400 to-blue-400 bg-clip-text text-transparent">
                                    {data.overview.total_businesses.toLocaleString()}
                                </span>
                            </div>
                            <h3 className="text-gray-400 text-sm uppercase tracking-wide">Total Businesses in Pipeline</h3>
                        </div>

                        <div className="group bg-gradient-to-br from-gray-800/50 to-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6 hover:border-blue-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-blue-500/20 rounded-lg group-hover:bg-blue-500/30 transition-colors">
                                    <ChartBarIcon />
                                </div>
                                <span className="text-3xl md:text-4xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
                                    {data.overview.total_leads_in_pipeline.enrichment_coverage_pct}%
                                </span>
                            </div>
                            <h3 className="text-gray-400 text-sm uppercase tracking-wide">Lead Enrichment Coverage</h3>
                            <p className="text-xs text-gray-500 mt-2">
                                {data.overview.total_leads_in_pipeline.with_owner} enriched / {data.overview.total_leads_in_pipeline.without_owner} pending
                            </p>
                        </div>
                    </div>
                </div>

                {/* Predictive Revenue Intelligence */}
                {forecastData && (
                    <div className="mb-8 border border-indigo-500/30 bg-indigo-950/20 rounded-2xl p-6 relative overflow-hidden">
                        <div className="absolute top-0 left-0 w-1 h-full bg-gradient-to-b from-indigo-500 to-purple-500 shadow-[0_0_15px_rgba(99,102,241,0.5)]"></div>
                        <h2 className="text-xl font-bold mb-4 flex items-center gap-2 text-indigo-100">
                            <ClockIcon />
                            Revenue Intelligence (7-Day Forecast)
                        </h2>

                        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                            <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
                                <p className="text-sm text-slate-400 font-mono mb-1">Active Pipeline</p>
                                <p className="text-2xl font-bold text-slate-200">{forecastData.pipeline_size.toLocaleString()}</p>
                            </div>

                            <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800">
                                <p className="text-sm text-slate-400 font-mono mb-1">Reply Velocity (7d)</p>
                                <p className="text-2xl font-bold text-slate-200">{forecastData.velocity_7d.replies}</p>
                            </div>

                            <div className="bg-slate-900/50 rounded-xl p-4 border border-indigo-900/50">
                                <p className="text-sm text-indigo-300 font-mono mb-1">Predicted Bookings</p>
                                <p className="text-3xl font-bold text-indigo-400">{forecastData.forecast.predicted_weekly_bookings}</p>
                            </div>

                            <div className="bg-slate-900/50 rounded-xl p-4 border border-slate-800 flex flex-col justify-center">
                                <div className="flex justify-between text-sm mb-1">
                                    <span className="text-slate-400">Health Score</span>
                                    <span className="font-semibold text-emerald-400">{forecastData.forecast.pipeline_health_score}%</span>
                                </div>
                                <div className="h-2 bg-slate-800 rounded-full overflow-hidden">
                                    <div
                                        className="h-full bg-emerald-500 rounded-full"
                                        style={{ width: `${forecastData.forecast.pipeline_health_score}%` }}
                                    ></div>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Data Quality Metrics */}
                <div className="mb-8">
                    <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                        <ServerIcon />
                        Data Quality Metrics
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div className="group bg-gradient-to-br from-gray-800/50 to-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6 hover:border-cyan-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-cyan-500/20">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-cyan-500/20 rounded-lg group-hover:bg-cyan-500/30 transition-colors">
                                    <MailIcon />
                                </div>
                                <span className="text-2xl md:text-3xl font-bold text-cyan-400">
                                    {data.data_quality.businesses_with_email.toLocaleString()}
                                </span>
                            </div>
                            <h3 className="text-gray-400 text-sm uppercase tracking-wide">Emails Captured</h3>
                            <div className="mt-2 h-2 bg-gray-700/50 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all duration-500"
                                    style={{ width: `${(data.data_quality.businesses_with_email / data.overview.total_businesses) * 100}%` }}
                                ></div>
                            </div>
                        </div>

                        <div className="group bg-gradient-to-br from-gray-800/50 to-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6 hover:border-purple-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-purple-500/20">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-purple-500/20 rounded-lg group-hover:bg-purple-500/30 transition-colors">
                                    <GlobeIcon />
                                </div>
                                <span className="text-2xl md:text-3xl font-bold text-purple-400">
                                    {data.data_quality.businesses_with_website.toLocaleString()}
                                </span>
                            </div>
                            <h3 className="text-gray-400 text-sm uppercase tracking-wide">Websites Found</h3>
                            <div className="mt-2 h-2 bg-gray-700/50 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                                    style={{ width: `${(data.data_quality.businesses_with_website / data.overview.total_businesses) * 100}%` }}
                                ></div>
                            </div>
                        </div>

                        <div className="group bg-gradient-to-br from-gray-800/50 to-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6 hover:border-blue-500/50 transition-all duration-300 hover:shadow-lg hover:shadow-blue-500/20">
                            <div className="flex items-center justify-between mb-4">
                                <div className="p-3 bg-blue-500/20 rounded-lg group-hover:bg-blue-500/30 transition-colors">
                                    <UserCircleIcon />
                                </div>
                                <span className="text-2xl md:text-3xl font-bold text-blue-400">
                                    {data.data_quality.businesses_with_owner_name.toLocaleString()}
                                </span>
                            </div>
                            <h3 className="text-gray-400 text-sm uppercase tracking-wide">Owner Names Enriched</h3>
                            <div className="mt-2 h-2 bg-gray-700/50 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-blue-500 to-indigo-500 rounded-full transition-all duration-500"
                                    style={{ width: `${(data.data_quality.businesses_with_owner_name / data.overview.total_businesses) * 100}%` }}
                                ></div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Scraper Health Status */}
                <div className="mb-8">
                    <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                        <ServerIcon />
                        Scraper Health Status
                    </h2>
                    <div className="bg-gradient-to-br from-gray-800/50 to-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <div className="flex items-center gap-3 mb-4">
                                    <div className={`flex items-center gap-2 px-4 py-2 rounded-lg border ${getHealthColor(data.scraper_health.status)}`}>
                                        <div className={`w-3 h-3 rounded-full ${getHealthDotColor(data.scraper_health.status)} animate-pulse`}></div>
                                        <span className="font-semibold uppercase text-sm">${data.scraper_health.status}</span>
                                    </div>
                                </div>
                                <div className="space-y-3">
                                    <div>
                                        <div className="flex justify-between text-sm mb-1">
                                            <span className="text-gray-400">Health Score</span>
                                            <span className="font-semibold">{data.scraper_health.health_score}%</span>
                                        </div>
                                        <div className="h-3 bg-gray-700/50 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all duration-500 ${data.scraper_health.health_score >= 80 ? 'bg-gradient-to-r from-green-500 to-emerald-500' :
                                                    data.scraper_health.health_score >= 50 ? 'bg-gradient-to-r from-yellow-500 to-orange-500' :
                                                        'bg-gradient-to-r from-red-500 to-pink-500'
                                                    }`}
                                                style={{ width: `${data.scraper_health.health_score}%` }}
                                            ></div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div className="grid grid-cols-1 gap-4">
                                <div className="bg-gray-700/30 rounded-lg p-4">
                                    <p className="text-gray-400 text-sm mb-1">Unresolved Errors</p>
                                    <p className="text-2xl font-bold text-red-400">{data.scraper_health.unresolved_errors}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recent Errors */}
                {data.scraper_health.recent_errors && data.scraper_health.recent_errors.length > 0 && (
                    <div className="mb-8">
                        <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                            <ExclamationIcon />
                            Recent System Errors
                        </h2>
                        <div className="bg-gradient-to-br from-gray-800/50 to-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl overflow-hidden">
                            <div className="overflow-x-auto">
                                <table className="w-full">
                                    <thead className="bg-gray-700/30">
                                        <tr>
                                            <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Timestamp</th>
                                            <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Source</th>
                                            <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Error Type</th>
                                            <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Message</th>
                                            <th className="px-6 py-4 text-left text-xs font-semibold text-gray-400 uppercase tracking-wider">Severity</th>
                                        </tr>
                                    </thead>
                                    <tbody className="divide-y divide-gray-700/50">
                                        {data.scraper_health.recent_errors.map((error: RecentError, index: number) => (
                                            <tr key={index} className="hover:bg-gray-700/20 transition-colors">
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-300">
                                                    {new Date(error.created_at).toLocaleString()}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-400">
                                                    {error.source}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className="px-3 py-1 text-xs font-semibold rounded-full bg-red-500/20 text-red-400 border border-red-500/50">
                                                        {error.error_type}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-sm text-gray-300 max-w-md truncate">
                                                    {error.error_message}
                                                </td>
                                                <td className="px-6 py-4 whitespace-nowrap">
                                                    <span className={`px-3 py-1 text-xs font-semibold rounded-full ${error.severity === 'critical' ? 'bg-red-500/20 text-red-400 border border-red-500/50' :
                                                        error.severity === 'warning' ? 'bg-yellow-500/20 text-yellow-400 border border-yellow-500/50' :
                                                            'bg-blue-500/20 text-blue-400 border border-blue-500/50'
                                                        }`}>
                                                        {error.severity}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                )}

                {/* Vibe Summary Stats */}
                <div className="mb-8">
                    <h2 className="text-2xl font-semibold mb-4 flex items-center gap-2">
                        <ChartBarIcon />
                        AI Vibe Synthesis
                    </h2>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                        <div className="bg-gradient-to-br from-gray-800/50 to-gray-800/30 backdrop-blur-xl border border-gray-700/50 rounded-2xl p-6">
                            <h3 className="text-gray-400 text-sm uppercase tracking-wide mb-2">Vibe Summaries Generated</h3>
                            <p className="text-3xl font-bold text-purple-400">{data.overview.total_vibe_summaries_generated.toLocaleString()}</p>
                            <div className="mt-2 h-2 bg-gray-700/50 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all duration-500"
                                    style={{ width: `${data.overview.vibe_coverage_pct}%` }}
                                ></div>
                            </div>
                            <p className="text-xs text-gray-500 mt-2">{data.overview.vibe_coverage_pct}% coverage</p>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="text-center text-gray-500 text-sm mt-8">
                    <p>Auto-refreshing every 60 seconds • Powered by Sovereign Empire API</p>
                </div>
            </div>

            <style jsx>{`
        @keyframes gradient {
          0%, 100% { background-position: 0% 50%; }
          50% { background-position: 100% 50%; }
        }
        .animate-gradient {
          background-size: 200% 200%;
          animation: gradient 3s ease infinite;
        }
      `}</style>
        </div>
    );
};

export default Dashboard;
