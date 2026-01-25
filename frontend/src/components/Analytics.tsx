import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import {
    PieChart, Pie, Cell, ResponsiveContainer,
    BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
    AreaChart, Area
} from 'recharts';
import { ArrowLeft, Bird, TrendingUp, Clock, Target, Activity, Shield, AlertTriangle, CheckCircle } from 'lucide-react';
import { Card } from './ui/Card';

// Color palette for charts
const COLORS = ['#1e40af', '#0ea5e9', '#f97316', '#22c55e', '#a855f7', '#ec4899', '#14b8a6', '#eab308', '#ef4444', '#6366f1', '#84cc16', '#f43f5e'];

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

// Population safety analysis based on hourly activity
function analyzePopulationSafety(hourlyData: HourlyData[]) {
    if (hourlyData.length === 0) return null;

    const totalActivity = hourlyData.reduce((sum, h) => sum + h.count, 0);
    const avgActivity = totalActivity / hourlyData.length;

    // Find peak hours (above average)
    const peakHours = hourlyData.filter(h => h.count > avgActivity).map(h => h.hour);

    // Find quiet hours (below half of average)
    const quietHours = hourlyData.filter(h => h.count < avgActivity / 2).map(h => h.hour);

    // Dawn chorus (5-8 AM)
    const dawnActivity = hourlyData.filter(h => {
        const hour = parseInt(h.hour);
        return hour >= 5 && hour <= 8;
    }).reduce((sum, h) => sum + h.count, 0);

    // Calculate health score (0-100)
    // More activity during dawn = healthier ecosystem
    const dawnRatio = dawnActivity / Math.max(totalActivity, 1);
    const diversityScore = peakHours.length >= 4 ? 30 : peakHours.length * 7;
    const activityScore = Math.min(totalActivity / 10, 40);
    const dawnScore = dawnRatio * 100 * 0.3;

    const healthScore = Math.round(activityScore + diversityScore + dawnScore);

    let status: 'healthy' | 'moderate' | 'concerning';
    let message: string;

    if (healthScore >= 70) {
        status = 'healthy';
        message = 'Strong bird activity indicates a healthy ecosystem with good biodiversity.';
    } else if (healthScore >= 40) {
        status = 'moderate';
        message = 'Moderate bird activity. Consider monitoring for changes in habitat conditions.';
    } else {
        status = 'concerning';
        message = 'Low bird activity detected. This may indicate environmental stressors.';
    }

    return {
        healthScore,
        status,
        message,
        peakHours: peakHours.slice(0, 4),
        quietHours: quietHours.slice(0, 4),
        dawnActivity,
        totalActivity
    };
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

    const populationAnalysis = analyzePopulationSafety(hourlyData);

    if (loading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center bg-sand-light">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-coastal-blue border-t-transparent"></div>
            </div>
        );
    }

    return (
        <section className="bg-sand-light min-h-screen py-12">
            <div className="max-w-7xl mx-auto px-6">
                {/* Header */}
                <div className="mb-10">
                    <Link to="/" className="flex items-center gap-2 text-white font-bold hover:text-sun-yellow mb-4 transition-colors group">
                        <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                        Back to Dashboard
                    </Link>
                    <h1 className="text-3xl md:text-4xl font-display font-bold text-ink-black">Analytics Dashboard</h1>
                    <p className="text-ink-gray mt-2 font-body">Insights and trends from your bird monitoring data</p>
                </div>

                {/* Summary Cards */}
                {summary && (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
                        <Card
                            variant="custom"
                            className="p-6 text-white"
                            style={{ background: 'linear-gradient(to bottom right, #007AFF, #0056B3)' }}
                        >
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

                        <Card
                            variant="custom"
                            className="p-6 text-white"
                            style={{ background: 'linear-gradient(to bottom right, #10B981, #059669)' }}
                        >
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

                        <Card
                            variant="custom"
                            className="p-6 text-white"
                            style={{ background: 'linear-gradient(to bottom right, #FF9500, #FF453A)' }}
                        >
                            <div className="flex items-center gap-4">
                                <div className="p-3 bg-white/20 rounded-xl">
                                    <Target className="w-6 h-6" />
                                </div>
                                <div>
                                    <p className="text-orange-100 text-sm font-medium">Avg Confidence</p>
                                    <p className="text-3xl font-bold">{summary.avg_confidence}%</p>
                                </div>
                            </div>
                        </Card>

                        <Card
                            variant="custom"
                            className="p-6 text-white"
                            style={{ background: 'linear-gradient(to bottom right, #8B5CF6, #7C3AED)' }}
                        >
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

                {/* Population Safety Analysis */}
                {populationAnalysis && (
                    <Card className="p-6 mb-8">
                        <h3 className="text-xl font-display font-bold text-ink-black mb-6 flex items-center gap-2">
                            <Shield className="w-5 h-5 text-coastal-blue" />
                            Population Health Analysis
                        </h3>

                        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                            {/* Health Score */}
                            <div className="text-center">
                                <div className={`w-32 h-32 mx-auto rounded-full border-8 flex items-center justify-center mb-4 ${populationAnalysis.status === 'healthy' ? 'border-green-500 bg-green-50' :
                                    populationAnalysis.status === 'moderate' ? 'border-amber-500 bg-amber-50' :
                                        'border-red-500 bg-red-50'
                                    }`}>
                                    <span className={`text-4xl font-display font-bold ${populationAnalysis.status === 'healthy' ? 'text-green-600' :
                                        populationAnalysis.status === 'moderate' ? 'text-amber-600' :
                                            'text-red-600'
                                        }`}>
                                        {populationAnalysis.healthScore}
                                    </span>
                                </div>
                                <div className="flex items-center justify-center gap-2">
                                    {populationAnalysis.status === 'healthy' ? (
                                        <CheckCircle className="w-5 h-5 text-green-500" />
                                    ) : populationAnalysis.status === 'moderate' ? (
                                        <AlertTriangle className="w-5 h-5 text-amber-500" />
                                    ) : (
                                        <AlertTriangle className="w-5 h-5 text-red-500" />
                                    )}
                                    <span className={`font-bold uppercase text-sm ${populationAnalysis.status === 'healthy' ? 'text-green-600' :
                                        populationAnalysis.status === 'moderate' ? 'text-amber-600' :
                                            'text-red-600'
                                        }`}>
                                        {populationAnalysis.status}
                                    </span>
                                </div>
                            </div>

                            {/* Analysis Details */}
                            <div className="md:col-span-2">
                                <p className="text-ink-gray font-body mb-4">{populationAnalysis.message}</p>

                                <div className="grid grid-cols-2 gap-4">
                                    <div className="bg-coastal-blue/10 rounded-lg p-4">
                                        <p className="text-sm font-bold text-coastal-blue mb-2">Peak Activity Hours</p>
                                        <p className="text-ink-black font-body">
                                            {populationAnalysis.peakHours.length > 0
                                                ? populationAnalysis.peakHours.join(', ')
                                                : 'No peak hours identified'}
                                        </p>
                                    </div>
                                    <div className="bg-amber-500/10 rounded-lg p-4">
                                        <p className="text-sm font-bold text-amber-600 mb-2">Dawn Chorus Activity</p>
                                        <p className="text-ink-black font-body">
                                            {populationAnalysis.dawnActivity} detections (5-8 AM)
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </Card>
                )}

                {/* Charts Row 1 */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
                    {/* Species Distribution - With Legend */}
                    <Card className="p-6">
                        <h3 className="text-xl font-display font-bold text-ink-black mb-6 flex items-center gap-2">
                            <Bird className="w-5 h-5 text-coastal-blue" />
                            Species Distribution
                        </h3>
                        <div className="flex flex-col lg:flex-row gap-4">
                            <div className="h-[250px] flex-1">
                                <ResponsiveContainer width="100%" height="100%">
                                    <PieChart>
                                        <Pie
                                            data={speciesData}
                                            cx="50%"
                                            cy="50%"
                                            innerRadius={50}
                                            outerRadius={90}
                                            fill="#8884d8"
                                            dataKey="value"
                                            paddingAngle={2}
                                        >
                                            {speciesData.map((_, index) => (
                                                <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                                            ))}
                                        </Pie>
                                        <Tooltip />
                                    </PieChart>
                                </ResponsiveContainer>
                            </div>
                            {/* Legend */}
                            <div className="flex-1 max-h-[250px] overflow-y-auto">
                                <div className="space-y-2">
                                    {speciesData.slice(0, 10).map((species, index) => (
                                        <div key={species.name} className="flex items-center gap-2 text-sm">
                                            <div
                                                className="w-3 h-3 rounded-full flex-shrink-0"
                                                style={{ backgroundColor: COLORS[index % COLORS.length] }}
                                            />
                                            <span className="text-ink-gray truncate flex-1">{species.name}</span>
                                            <span className="font-bold text-ink-black">{species.value}</span>
                                        </div>
                                    ))}
                                    {speciesData.length > 10 && (
                                        <p className="text-xs text-ink-gray">+{speciesData.length - 10} more species</p>
                                    )}
                                </div>
                            </div>
                        </div>
                    </Card>

                    {/* Hourly Activity */}
                    <Card className="p-6">
                        <h3 className="text-xl font-display font-bold text-ink-black mb-6 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-coastal-blue" />
                            Activity by Hour
                        </h3>
                        <div className="h-[300px]">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={hourlyData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                                    <XAxis dataKey="hour" tick={{ fontSize: 11 }} />
                                    <YAxis tick={{ fontSize: 12 }} />
                                    <Tooltip />
                                    <Area type="monotone" dataKey="count" stroke="#007AFF" fill="#007AFF" fillOpacity={0.3} />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </Card>
                </div>

                {/* Detection Trends */}
                <Card className="p-6 mb-8">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-6">
                        <h3 className="text-xl font-display font-bold text-ink-black flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-coastal-blue" />
                            Detection Trends
                        </h3>
                        <div className="flex bg-white border-2 border-ink-black rounded-lg p-1 shadow-brutal">
                            {(['day', 'week', 'month'] as const).map((period) => (
                                <button
                                    key={period}
                                    onClick={() => setTrendPeriod(period)}
                                    className={`px-4 py-2 rounded-md text-sm font-bold transition-all ${trendPeriod === period
                                        ? 'bg-sun-yellow text-ink-black'
                                        : 'text-ink-gray hover:bg-sand-light'
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
                                <Bar dataKey="count" name="Detections" fill="#007AFF" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </Card>

                {/* Confidence Distribution */}
                <Card className="p-6">
                    <h3 className="text-xl font-display font-bold text-ink-black mb-6 flex items-center gap-2">
                        <Target className="w-5 h-5 text-coastal-blue" />
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
            </div>
        </section>
    );
}
