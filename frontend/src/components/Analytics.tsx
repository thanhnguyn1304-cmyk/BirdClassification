import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import {
    PieChart, Pie, Cell, ResponsiveContainer,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    LineChart, Line, Area, AreaChart
} from 'recharts';
import { ArrowLeft, Bird, TrendingUp, Clock, Target, Activity } from 'lucide-react';
import { Card } from './ui/Card';

// Color palette for charts
const COLORS = ['#1e40af', '#0ea5e9', '#f97316', '#22c55e', '#a855f7', '#ec4899', '#14b8a6', '#eab308'];

interface SummaryData {
    total_detections: number;
    unique_species: number;
    avg_confidence: number;
    most_recent: {
        timestamp: string | null;
        species: string | null;
    };
}

interface SpeciesData {
    name: string;
    value: number;
}

interface TrendData {
    date: string;
    count: number;
    species: Record<string, number>;
}

interface HourlyData {
    hour: string;
    count: number;
}

interface ConfidenceData {
    range: string;
    count: number;
}

export function Analytics() {
    const [summary, setSummary] = useState<SummaryData | null>(null);
    const [speciesData, setSpeciesData] = useState<SpeciesData[]>([]);
    const [trendsData, setTrendsData] = useState<TrendData[]>([]);
    const [hourlyData, setHourlyData] = useState<HourlyData[]>([]);
    const [confidenceData, setConfidenceData] = useState<ConfidenceData[]>([]);
    const [loading, setLoading] = useState(true);
    const [trendPeriod, setTrendPeriod] = useState<'day' | 'week' | 'month'>('day');

    useEffect(() => {
        const fetchAnalytics = async () => {
            try {
                const [summaryRes, speciesRes, hourlyRes, confidenceRes] = await Promise.all([
                    axios.get('/api/analytics/summary'),
                    axios.get('/api/analytics/species-distribution'),
                    axios.get('/api/analytics/hourly-activity'),
                    axios.get('/api/analytics/confidence-distribution')
                ]);

                setSummary(summaryRes.data);
                setSpeciesData(speciesRes.data);
                setHourlyData(hourlyRes.data);
                setConfidenceData(confidenceRes.data);
            } catch (error) {
                console.error("Failed to fetch analytics:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchAnalytics();
    }, []);

    useEffect(() => {
        const fetchTrends = async () => {
            try {
                const res = await axios.get(`/api/analytics/trends?period=${trendPeriod}`);
                setTrendsData(res.data);
            } catch (error) {
                console.error("Failed to fetch trends:", error);
            }
        };
        fetchTrends();
    }, [trendPeriod]);

    if (loading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-kingfisher-royal"></div>
            </div>
        );
    }

    return (
        <section className="max-w-7xl mx-auto px-6 py-12">
            {/* Header */}
            <div className="mb-10">
                <Link to="/" className="flex items-center gap-2 text-slate-500 hover:text-kingfisher-royal mb-4 transition-colors group">
                    <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                    Back to Dashboard
                </Link>
                <h1 className="text-3xl md:text-4xl font-display font-bold text-kingfisher-midnight">Analytics Dashboard</h1>
                <p className="text-slate-500 mt-2">Insights and trends from your bird monitoring data</p>
            </div>

            {/* Summary Cards */}
            {summary && (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                    <Card className="p-6 bg-gradient-to-br from-blue-500 to-blue-600 text-white">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-white/20 rounded-xl">
                                <Bird className="w-6 h-6" />
                            </div>
                            <div>
                                <p className="text-blue-100 text-sm font-medium">Total Detections</p>
                                <p className="text-3xl font-bold">{summary.total_detections}</p>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6 bg-gradient-to-br from-emerald-500 to-emerald-600 text-white">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-white/20 rounded-xl">
                                <Activity className="w-6 h-6" />
                            </div>
                            <div>
                                <p className="text-emerald-100 text-sm font-medium">Unique Species</p>
                                <p className="text-3xl font-bold">{summary.unique_species}</p>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6 bg-gradient-to-br from-amber-500 to-amber-600 text-white">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-white/20 rounded-xl">
                                <Target className="w-6 h-6" />
                            </div>
                            <div>
                                <p className="text-amber-100 text-sm font-medium">Avg Confidence</p>
                                <p className="text-3xl font-bold">{summary.avg_confidence}%</p>
                            </div>
                        </div>
                    </Card>

                    <Card className="p-6 bg-gradient-to-br from-purple-500 to-purple-600 text-white">
                        <div className="flex items-center gap-4">
                            <div className="p-3 bg-white/20 rounded-xl">
                                <Clock className="w-6 h-6" />
                            </div>
                            <div>
                                <p className="text-purple-100 text-sm font-medium">Most Recent</p>
                                <p className="text-lg font-bold truncate">{summary.most_recent.species || 'N/A'}</p>
                            </div>
                        </div>
                    </Card>
                </div>
            )}

            {/* Charts Row 1 */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                {/* Species Distribution Pie Chart */}
                <Card className="p-6">
                    <h3 className="text-xl font-bold text-kingfisher-midnight mb-6 flex items-center gap-2">
                        <Bird className="w-5 h-5 text-kingfisher-royal" />
                        Species Distribution
                    </h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <PieChart>
                                <Pie
                                    data={speciesData}
                                    cx="50%"
                                    cy="50%"
                                    labelLine={false}
                                    label={({ name, percent }) => `${name} (${(percent * 100).toFixed(0)}%)`}
                                    outerRadius={100}
                                    fill="#8884d8"
                                    dataKey="value"
                                >
                                    {speciesData.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                    ))}
                                </Pie>
                                <Tooltip />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                {/* Hourly Activity */}
                <Card className="p-6">
                    <h3 className="text-xl font-bold text-kingfisher-midnight mb-6 flex items-center gap-2">
                        <Clock className="w-5 h-5 text-kingfisher-royal" />
                        Activity by Hour
                    </h3>
                    <div className="h-[300px]">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={hourlyData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                <XAxis dataKey="hour" tick={{ fontSize: 12 }} />
                                <YAxis tick={{ fontSize: 12 }} />
                                <Tooltip />
                                <Area type="monotone" dataKey="count" stroke="#1e40af" fill="#3b82f6" fillOpacity={0.3} />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </Card>
            </div>

            {/* Detection Trends */}
            <Card className="p-6 mb-8">
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                    <h3 className="text-xl font-bold text-kingfisher-midnight flex items-center gap-2">
                        <TrendingUp className="w-5 h-5 text-kingfisher-royal" />
                        Detection Trends
                    </h3>
                    <div className="flex bg-slate-100 p-1 rounded-lg">
                        {(['day', 'week', 'month'] as const).map((period) => (
                            <button
                                key={period}
                                onClick={() => setTrendPeriod(period)}
                                className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${trendPeriod === period
                                        ? 'bg-white shadow text-kingfisher-royal'
                                        : 'text-slate-500 hover:text-slate-700'
                                    }`}
                            >
                                {period.charAt(0).toUpperCase() + period.slice(1)}
                            </button>
                        ))}
                    </div>
                </div>
                <div className="h-[350px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={trendsData}>
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis dataKey="date" tick={{ fontSize: 11 }} angle={-45} textAnchor="end" height={80} />
                            <YAxis tick={{ fontSize: 12 }} />
                            <Tooltip />
                            <Legend />
                            <Bar dataKey="count" name="Detections" fill="#1e40af" radius={[4, 4, 0, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </Card>

            {/* Confidence Distribution */}
            <Card className="p-6">
                <h3 className="text-xl font-bold text-kingfisher-midnight mb-6 flex items-center gap-2">
                    <Target className="w-5 h-5 text-kingfisher-royal" />
                    Confidence Score Distribution
                </h3>
                <div className="h-[300px]">
                    <ResponsiveContainer width="100%" height="100%">
                        <BarChart data={confidenceData} layout="vertical">
                            <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                            <XAxis type="number" tick={{ fontSize: 12 }} />
                            <YAxis type="category" dataKey="range" tick={{ fontSize: 12 }} width={80} />
                            <Tooltip />
                            <Bar dataKey="count" name="Detections" fill="#22c55e" radius={[0, 4, 4, 0]} />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            </Card>
        </section>
    );
}
