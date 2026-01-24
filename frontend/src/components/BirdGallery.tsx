import { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import type { BirdDetection, SpeciesInfo } from '../types/bird';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Calendar, Layers, Grid, Maximize2, Bird, MapPin, X, Clock, Activity } from 'lucide-react';
import { cn } from '../lib/utils';

export function BirdGallery() {
    const [detections, setDetections] = useState<BirdDetection[]>([]);
    const [speciesList, setSpeciesList] = useState<SpeciesInfo[]>([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'sessions' | 'species'>('sessions');
    const [selectedSpecies, setSelectedSpecies] = useState<SpeciesInfo | null>(null);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
            try {
                const [detectionsRes, speciesRes] = await Promise.all([
                    axios.get('/api/detections'),
                    axios.get('/api/species-summary')
                ]);
                setDetections(detectionsRes.data);
                setSpeciesList(speciesRes.data);
            } catch (error) {
                console.error("Failed to fetch data:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 10000);
        return () => clearInterval(interval);
    }, []);

    // Get detections for a specific species (for the modal)
    const getDetectionsForSpecies = (speciesName: string) => {
        return detections
            .filter(d => d.species === speciesName)
            .sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
    };

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
                {/* Header & Tabs */}
                <div className="flex flex-col md:flex-row items-end justify-between mb-10 pb-6 gap-4">
                    <div>
                        <h2 className="text-4xl md:text-5xl font-display font-bold text-ink-black">
                            Recent Detections
                        </h2>
                        <p className="text-ink-gray mt-2 font-body">Live stream of identified bird calls</p>
                    </div>

                    {/* Tab Switcher */}
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

                        {/* SPECIES VIEW - Simple Cards */}
                        {activeTab === 'species' && speciesList.map((species) => (
                            <div key={species.name}>
                                <Card
                                    className="h-full flex flex-col text-center cursor-pointer"
                                    onClick={() => setSelectedSpecies(species)}
                                >
                                    <div className="w-28 h-28 mx-auto rounded-full overflow-hidden border-4 border-ink-black shadow-brutal mb-4 bg-white">
                                        <img
                                            src={species.image_url || '/placeholder-bird.png'}
                                            alt={species.name}
                                            className="w-full h-full object-cover"
                                        />
                                    </div>
                                    <h3 className="text-xl font-display font-bold text-ink-black mb-2">{species.name}</h3>
                                    <div className="flex justify-center items-center gap-2 mb-4">
                                        <span className="text-4xl font-display font-bold text-coastal-blue">{species.detection_count}</span>
                                        <span className="text-ink-gray text-sm uppercase tracking-wide font-bold">Detections</span>
                                    </div>
                                    <div className="mt-auto text-sm text-ink-gray border-t-2 border-ink-black/10 pt-3 font-body">
                                        Last seen: {new Date(species.last_seen).toLocaleDateString()}
                                    </div>
                                </Card>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* SPECIES DETAIL MODAL */}
            {selectedSpecies && (
                <div
                    className="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm"
                    onClick={() => setSelectedSpecies(null)}
                >
                    <div
                        className="relative max-w-4xl w-full bg-sand-light border-4 border-ink-black rounded-2xl overflow-hidden shadow-brutal-xl max-h-[90vh] flex flex-col"
                        onClick={e => e.stopPropagation()}
                    >
                        {/* Header */}
                        <div className="bg-coastal-blue p-6 text-white relative">
                            <button
                                onClick={() => setSelectedSpecies(null)}
                                className="absolute top-4 right-4 p-2 bg-white/20 hover:bg-white/30 rounded-full transition-colors"
                            >
                                <X className="w-6 h-6" />
                            </button>

                            <div className="flex items-center gap-6">
                                <div className="w-24 h-24 rounded-full overflow-hidden border-4 border-white shadow-lg bg-white flex-shrink-0">
                                    <img
                                        src={selectedSpecies.image_url || '/placeholder-bird.png'}
                                        alt={selectedSpecies.name}
                                        className="w-full h-full object-cover"
                                    />
                                </div>
                                <div>
                                    <h2 className="text-3xl font-display font-bold">{selectedSpecies.name}</h2>
                                    {selectedSpecies.region && (
                                        <div className="flex items-center gap-2 mt-2 text-white/80">
                                            <MapPin className="w-4 h-4" />
                                            <span>{selectedSpecies.region}</span>
                                        </div>
                                    )}
                                </div>
                            </div>
                        </div>

                        {/* Content */}
                        <div className="flex-1 overflow-y-auto p-6">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                                {/* Left Column - Info */}
                                <div>
                                    {/* Description */}
                                    {selectedSpecies.description && (
                                        <div className="mb-6">
                                            <h3 className="text-lg font-display font-bold text-ink-black mb-2">About</h3>
                                            <p className="text-ink-gray font-body text-sm leading-relaxed">
                                                {selectedSpecies.description}
                                            </p>
                                        </div>
                                    )}

                                    {/* Stats */}
                                    <div className="bg-white border-2 border-ink-black rounded-xl p-4 shadow-brutal">
                                        <h3 className="text-lg font-display font-bold text-ink-black mb-4">Statistics</h3>
                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="text-center">
                                                <div className="text-3xl font-display font-bold text-coastal-blue">{selectedSpecies.detection_count}</div>
                                                <div className="text-xs text-ink-gray uppercase">Total Detections</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-3xl font-display font-bold text-green-600">{selectedSpecies.avg_confidence}%</div>
                                                <div className="text-xs text-ink-gray uppercase">Avg Confidence</div>
                                            </div>
                                        </div>
                                        <div className="mt-4 pt-4 border-t border-ink-black/10 text-sm text-ink-gray">
                                            <div className="flex justify-between">
                                                <span>First detected:</span>
                                                <span className="font-bold">{new Date(selectedSpecies.first_seen).toLocaleDateString()}</span>
                                            </div>
                                            <div className="flex justify-between mt-1">
                                                <span>Last detected:</span>
                                                <span className="font-bold">{new Date(selectedSpecies.last_seen).toLocaleDateString()}</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>

                                {/* Right Column - Activity Log */}
                                <div>
                                    <div className="bg-white border-2 border-ink-black rounded-xl p-4 shadow-brutal">
                                        <h3 className="text-lg font-display font-bold text-ink-black mb-4 flex items-center gap-2">
                                            <Activity className="w-5 h-5 text-coastal-blue" />
                                            Activity Log
                                        </h3>
                                        <div className="space-y-3 max-h-[300px] overflow-y-auto">
                                            {getDetectionsForSpecies(selectedSpecies.name).map((detection, idx) => (
                                                <div key={detection.id || idx} className="flex items-start gap-3 p-3 bg-sand-light rounded-lg border border-ink-black/10">
                                                    <div className="p-2 bg-coastal-blue/10 rounded-lg">
                                                        <Clock className="w-4 h-4 text-coastal-blue" />
                                                    </div>
                                                    <div className="flex-1">
                                                        <div className="text-sm font-bold text-ink-black">
                                                            {new Date(detection.timestamp).toLocaleString()}
                                                        </div>
                                                        <div className="text-xs text-ink-gray mt-1">
                                                            Confidence: <span className={detection.confidence > 0.8 ? "text-green-600 font-bold" : "text-amber-600 font-bold"}>
                                                                {Math.round(detection.confidence * 100)}%
                                                            </span>
                                                        </div>
                                                        {detection.lat && detection.lon && (
                                                            <div className="flex items-center gap-1 text-xs text-ink-gray mt-1">
                                                                <MapPin className="w-3 h-3" />
                                                                <span>{detection.lat.toFixed(4)}, {detection.lon.toFixed(4)}</span>
                                                            </div>
                                                        )}
                                                    </div>
                                                    <Badge variant={detection.confidence > 0.8 ? "success" : "warning"} className="text-xs">
                                                        {Math.round(detection.confidence * 100)}%
                                                    </Badge>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </section>
    );
}
