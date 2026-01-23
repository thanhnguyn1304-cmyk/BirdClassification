import { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import type { BirdDetection } from '../types/bird';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Calendar, Layers, Grid, Maximize2, Bird } from 'lucide-react';
import { cn } from '../lib/utils';

export function BirdGallery() {
    const [detections, setDetections] = useState<BirdDetection[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'sessions' | 'species'>('sessions');
    const navigate = useNavigate();

    useEffect(() => {
        const fetchDetections = async () => {
            try {
                const response = await axios.get('/api/detections');
                setDetections(response.data);
            } catch (error) {
                console.error("Failed to fetch detections:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDetections();
        const interval = setInterval(fetchDetections, 10000);
        return () => clearInterval(interval);
    }, []);

    // Group by Species Logic - now includes bird_photo_url from Wikipedia
    const speciesGroups = detections.reduce((acc, bird) => {
        if (!acc[bird.species]) {
            acc[bird.species] = {
                count: 0,
                lastSeen: bird.timestamp,
                image: bird.single_image_url,
                birdPhoto: bird.bird_photo_url
            };
        }
        acc[bird.species].count += 1;
        if (new Date(bird.timestamp) > new Date(acc[bird.species].lastSeen)) {
            acc[bird.species].lastSeen = bird.timestamp;
            acc[bird.species].image = bird.single_image_url;
        }
        // Prefer bird_photo_url if available
        if (bird.bird_photo_url && !acc[bird.species].birdPhoto) {
            acc[bird.species].birdPhoto = bird.bird_photo_url;
        }
        return acc;
    }, {} as Record<string, { count: number; lastSeen: string; image: string; birdPhoto: string | null }>);

    // Group by Session (Image URL) Logic
    const sessionGroups = detections.reduce((acc, bird) => {
        const key = bird.image_url || 'unknown_session';

        if (!acc[key]) {
            acc[key] = {
                masterImage: bird.image_url,
                startTime: bird.timestamp,
                detections: []
            };
        }
        acc[key].detections.push(bird);
        if (new Date(bird.timestamp) < new Date(acc[key].startTime)) {
            acc[key].startTime = bird.timestamp;
        }
        return acc;
    }, {} as Record<string, { masterImage: string; startTime: string; detections: BirdDetection[] }>);

    if (loading) {
        return (
            <div className="min-h-[40vh] flex items-center justify-center bg-sand-light">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-coastal-blue border-t-transparent"></div>
            </div>
        );
    }

    return (
        <section id="gallery" className="bg-sand-light py-20">
            <div className="max-w-7xl mx-auto px-6">
                {/* Header & Tabs - Brutal Style */}
                <div className="flex flex-col md:flex-row items-end justify-between mb-10 pb-6 gap-4">
                    <div>
                        <h2 className="text-4xl md:text-5xl font-display font-bold text-ink-black">
                            Recent Detections
                        </h2>
                        <p className="text-ink-gray mt-2 font-body">Live stream of identified bird calls</p>
                    </div>

                    {/* Tab Switcher - Brutal Style */}
                    <div className="flex bg-white border-3 border-ink-black rounded-xl p-1 shadow-brutal">
                        <button
                            onClick={() => setActiveTab('sessions')}
                            className={cn(
                                "flex items-center gap-2 px-5 py-3 rounded-lg font-bold text-sm transition-all",
                                activeTab === 'sessions'
                                    ? "bg-sun-yellow text-ink-black"
                                    : "text-ink-gray hover:bg-sand-light"
                            )}
                        >
                            <Grid className="w-4 h-4" />
                            Sessions
                        </button>
                        <button
                            onClick={() => setActiveTab('species')}
                            className={cn(
                                "flex items-center gap-2 px-5 py-3 rounded-lg font-bold text-sm transition-all",
                                activeTab === 'species'
                                    ? "bg-sun-yellow text-ink-black"
                                    : "text-ink-gray hover:bg-sand-light"
                            )}
                        >
                            <Layers className="w-4 h-4" />
                            Species
                        </button>
                    </div>
                </div>

                {/* Content */}
                {detections.length === 0 ? (
                    <div className="text-center py-20 bg-white border-3 border-dashed border-ink-black rounded-2xl">
                        <Bird className="w-16 h-16 mx-auto text-ink-gray mb-4" />
                        <p className="text-2xl font-display text-ink-black">No birds detected yet.</p>
                        <p className="text-ink-gray mt-2 font-body">Start the monitoring system to see results.</p>
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                        {/* SESSIONS VIEW */}
                        {activeTab === 'sessions' && Object.entries(sessionGroups)
                            .sort(([, a], [, b]) => new Date(b.startTime).getTime() - new Date(a.startTime).getTime())
                            .map(([key, session]) => (
                                <div key={key}>
                                    <Card
                                        className="h-full flex flex-col cursor-pointer"
                                        onClick={() => navigate(`/session/${encodeURIComponent(session.masterImage)}`)}
                                    >
                                        <div className="relative aspect-video bg-ink-black overflow-hidden mb-4 rounded-lg border-2 border-ink-black">
                                            <img
                                                src={session.masterImage || session.detections[0].single_image_url}
                                                alt="Session Spectrogram"
                                                className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                            />
                                            <div className="absolute inset-0 bg-ink-black/60 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
                                                <div className="flex items-center gap-2 text-white font-bold bg-sun-yellow text-ink-black px-4 py-2 rounded-lg border-2 border-ink-black">
                                                    <Maximize2 className="w-5 h-5" />
                                                    View Session
                                                </div>
                                            </div>
                                            <div className="absolute top-3 right-3">
                                                <Badge variant="warning">
                                                    {session.detections.length} Detections
                                                </Badge>
                                            </div>
                                        </div>

                                        <div className="flex-1">
                                            <h3 className="text-xl font-display font-bold text-ink-black mb-2">Recording Session</h3>
                                            <div className="space-y-2 text-sm text-ink-gray font-body">
                                                <div className="flex items-center gap-2">
                                                    <Calendar className="w-4 h-4 text-coastal-blue" />
                                                    <span>{new Date(session.startTime).toLocaleString()}</span>
                                                </div>
                                                <div className="flex flex-wrap gap-1 mt-2">
                                                    {Array.from(new Set(session.detections.map(d => d.species))).slice(0, 3).map(species => (
                                                        <span key={species} className="text-xs bg-coastal-blue/10 text-coastal-blue font-bold px-2 py-1 rounded-full border border-coastal-blue/30">
                                                            {species}
                                                        </span>
                                                    ))}
                                                    {new Set(session.detections.map(d => d.species)).size > 3 && (
                                                        <span className="text-xs text-ink-gray px-2 py-1">+more</span>
                                                    )}
                                                </div>
                                            </div>
                                        </div>
                                    </Card>
                                </div>
                            ))}

                        {/* SPECIES VIEW - Uses Wikipedia bird photos when available */}
                        {activeTab === 'species' && Object.entries(speciesGroups).map(([species, data]) => (
                            <div key={species}>
                                <Card className="h-full flex flex-col text-center">
                                    <div className="w-32 h-32 mx-auto rounded-full overflow-hidden border-4 border-ink-black shadow-brutal mb-6 bg-white">
                                        <img
                                            src={data.birdPhoto || data.image}
                                            alt={species}
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                    <h3 className="text-2xl font-display font-bold text-ink-black mb-2">{species}</h3>
                                    <div className="flex justify-center items-center gap-2 mb-6">
                                        <span className="text-5xl font-display font-bold text-coastal-blue">{data.count}</span>
                                        <span className="text-ink-gray text-sm uppercase tracking-wide font-bold">Detections</span>
                                    </div>
                                    <div className="mt-auto text-sm text-ink-gray border-t-2 border-ink-black/20 pt-4 font-body">
                                        Last seen: {new Date(data.lastSeen).toLocaleDateString()}
                                    </div>
                                </Card>
                            </div>
                        ))}
                    </div>
                )}
            </div>
        </section>
    );
}
