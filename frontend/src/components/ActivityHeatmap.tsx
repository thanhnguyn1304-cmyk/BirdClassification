/**
 * ActivityHeatmap - A GitHub-style contribution calendar for bird detections
 * 
 * HOW IT WORKS:
 * 
 * 1. DATA STRUCTURE
 *    The backend returns 365 days of data, each with:
 *    - date: "2026-01-15"
 *    - count: number of detections (0-n)
 *    - weekday: 0-6 (Monday-Sunday)
 *    - week: 0-51 (which column in the grid)
 *    - level: 0-4 (intensity for coloring)
 * 
 * 2. LAYOUT (CSS Grid)
 *    The calendar is a grid with:
 *    - 7 rows (one per weekday: Mon-Sun)
 *    - 52-53 columns (one per week of the year)
 *    Each cell is a small square (10x10px)
 * 
 * 3. INTENSITY LEVELS
 *    Level 0: No activity (lightest color)
 *    Level 1: 1-25% of max (light)
 *    Level 2: 25-50% of max (medium)
 *    Level 3: 50-75% of max (darker)
 *    Level 4: 75-100% of max (darkest)
 * 
 * 4. POSITIONING
 *    Each day is placed at:
 *    - Column = week number (0-51)
 *    - Row = weekday (0=Mon, 6=Sun)
 */

import { useState, useEffect } from 'react';
import axios from 'axios';
import { Card } from './ui/Card';
import { Calendar } from 'lucide-react';

interface DayData {
    date: string;
    count: number;
    weekday: number;
    week: number;
    level: number;
}

interface HeatmapData {
    days: DayData[];
    max_count: number;
    total_days: number;
    total_detections: number;
}

// Color palette for intensity levels (like GitHub's green, but blue for birds)
const LEVEL_COLORS = [
    '#ebedf0',  // Level 0: No activity (gray)
    '#c6e5ff',  // Level 1: Light blue
    '#79c0ff',  // Level 2: Medium blue
    '#2e8fff',  // Level 3: Bright blue
    '#0056b3',  // Level 4: Deep blue
];

export function ActivityHeatmap() {
    const [data, setData] = useState<HeatmapData | null>(null);
    const [loading, setLoading] = useState(true);
    const [hoveredDay, setHoveredDay] = useState<DayData | null>(null);
    const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });

    useEffect(() => {
        const fetchHeatmap = async () => {
            try {
                const res = await axios.get('/api/analytics/calendar-heatmap');
                setData(res.data);
            } catch (error) {
                console.error('Failed to fetch heatmap data:', error);
            } finally {
                setLoading(false);
            }
        };

        // Initial fetch
        fetchHeatmap();

        // Short-polling: Refresh every 30 seconds
        // (Heatmap data changes less frequently than real-time detections)
        const interval = setInterval(fetchHeatmap, 30000);

        // Cleanup on unmount
        return () => clearInterval(interval);
    }, []);

    // Handle mouse hover for tooltip
    const handleMouseEnter = (day: DayData, event: React.MouseEvent) => {
        setHoveredDay(day);
        const rect = event.currentTarget.getBoundingClientRect();
        setTooltipPos({
            x: rect.left + rect.width / 2,
            y: rect.top - 10
        });
    };

    const handleMouseLeave = () => {
        setHoveredDay(null);
    };

    // Get month labels based on the data
    const getMonthLabels = () => {
        if (!data) return [];

        const months: { name: string; week: number }[] = [];
        let lastMonth = -1;

        for (const day of data.days) {
            const date = new Date(day.date);
            const month = date.getMonth();

            if (month !== lastMonth) {
                months.push({
                    name: date.toLocaleDateString('en-US', { month: 'short' }),
                    week: day.week
                });
                lastMonth = month;
            }
        }

        return months;
    };

    if (loading) {
        return (
            <Card className="p-6">
                <div className="flex items-center justify-center h-32">
                    <div className="animate-spin rounded-full h-8 w-8 border-4 border-coastal-blue border-t-transparent"></div>
                </div>
            </Card>
        );
    }

    if (!data) {
        return (
            <Card className="p-6">
                <p className="text-ink-gray">Failed to load heatmap data</p>
            </Card>
        );
    }

    const monthLabels = getMonthLabels();

    return (
        <Card className="p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-3">
                    <div className="p-2 bg-coastal-blue/10 rounded-lg">
                        <Calendar className="w-5 h-5 text-coastal-blue" />
                    </div>
                    <div>
                        <h3 className="font-bold text-ink-black">Detection Activity</h3>
                        <p className="text-sm text-ink-gray">
                            {data.total_detections} detections in the last year
                        </p>
                    </div>
                </div>

                {/* Legend */}
                <div className="flex items-center gap-2 text-sm text-ink-gray">
                    <span>Less</span>
                    {LEVEL_COLORS.map((color, i) => (
                        <div
                            key={i}
                            className="w-3 h-3 rounded-sm"
                            style={{ backgroundColor: color }}
                        />
                    ))}
                    <span>More</span>
                </div>
            </div>

            {/* Month Labels */}
            <div className="relative mb-2 ml-8">
                <div className="flex" style={{ width: '780px' }}>
                    {monthLabels.map((month, i) => (
                        <div
                            key={i}
                            className="text-xs text-ink-gray"
                            style={{
                                position: 'absolute',
                                left: `${month.week * 15}px`
                            }}
                        >
                            {month.name}
                        </div>
                    ))}
                </div>
            </div>

            {/* Heatmap Grid */}
            <div className="flex gap-2">
                {/* Weekday Labels */}
                <div className="flex flex-col justify-between text-xs text-ink-gray" style={{ height: '98px' }}>
                    <span>Mon</span>
                    <span>Wed</span>
                    <span>Fri</span>
                </div>

                {/* Grid Container */}
                <div className="overflow-x-auto">
                    <div
                        className="grid gap-[3px]"
                        style={{
                            gridTemplateRows: 'repeat(7, 12px)',
                            gridAutoFlow: 'column',
                            gridAutoColumns: '12px'
                        }}
                    >
                        {data.days.map((day, i) => (
                            <div
                                key={i}
                                className="rounded-sm cursor-pointer transition-all hover:ring-2 hover:ring-ink-black hover:ring-offset-1"
                                style={{
                                    width: '12px',
                                    height: '12px',
                                    backgroundColor: LEVEL_COLORS[day.level],
                                    gridRow: day.weekday + 1  // CSS grid is 1-indexed
                                }}
                                onMouseEnter={(e) => handleMouseEnter(day, e)}
                                onMouseLeave={handleMouseLeave}
                            />
                        ))}
                    </div>
                </div>
            </div>

            {/* Tooltip */}
            {hoveredDay && (
                <div
                    className="fixed z-50 px-3 py-2 bg-ink-black text-white text-sm rounded-lg shadow-lg pointer-events-none transform -translate-x-1/2 -translate-y-full"
                    style={{
                        left: tooltipPos.x,
                        top: tooltipPos.y
                    }}
                >
                    <div className="font-bold">{hoveredDay.count} detection{hoveredDay.count !== 1 ? 's' : ''}</div>
                    <div className="text-gray-300">
                        {new Date(hoveredDay.date).toLocaleDateString('en-US', {
                            weekday: 'short',
                            month: 'short',
                            day: 'numeric',
                            year: 'numeric'
                        })}
                    </div>
                    {/* Tooltip arrow */}
                    <div className="absolute left-1/2 bottom-0 transform -translate-x-1/2 translate-y-full">
                        <div className="border-8 border-transparent border-t-ink-black"></div>
                    </div>
                </div>
            )}
        </Card>
    );
}
