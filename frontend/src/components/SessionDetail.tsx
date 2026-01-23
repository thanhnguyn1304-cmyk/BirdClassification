import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import axios from 'axios';
import { ArrowLeft, Calendar, MapPin, Music, Grid, X, Maximize2 } from 'lucide-react';
import type { BirdDetection } from '../types/bird';
import { Card } from './ui/Card';
import { Badge } from './ui/Badge';
import { Button } from './ui/Button';

export function SessionDetail() {
    const { sessionId } = useParams<{ sessionId: string }>();
    const navigate = useNavigate();
    const [allDetections, setAllDetections] = useState<BirdDetection[]>([]);
    const [sessionDetections, setSessionDetections] = useState<BirdDetection[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedBird, setSelectedBird] = useState<BirdDetection | null>(null);

    // Decode session ID (which is the image_url)
    const masterImageUrl = sessionId ? decodeURIComponent(sessionId) : '';

    useEffect(() => {
        const fetchDetections = async () => {
            try {
                // Ideally, we'd have an API endpoint like /api/sessions/:id
                // But for now we fetch all and filter client-side as per plan
                const response = await axios.get('/api/detections');
                const data: BirdDetection[] = response.data;
                setAllDetections(data);

                if (masterImageUrl) {
                    const filtered = data.filter(d => d.image_url === masterImageUrl);
                    setSessionDetections(filtered);
                }
            } catch (error) {
                console.error("Failed to fetch detections:", error);
            } finally {
                setLoading(false);
            }
        };

        fetchDetections();
    }, [masterImageUrl]);

    if (loading) {
        return (
            <div className="min-h-[60vh] flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-kingfisher-royal"></div>
            </div>
        );
    }

    if (!sessionDetections.length) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-20 text-center">
                <h2 className="text-2xl font-bold text-slate-700">Session Not Found</h2>
                <Button onClick={() => navigate('/')} className="mt-4">Back to Gallery</Button>
            </div>
        );
    }

    // Determine session start time (earliest detection)
    const startTime = sessionDetections.reduce((earliest, current) => {
        return new Date(current.timestamp) < new Date(earliest) ? current.timestamp : earliest;
    }, sessionDetections[0].timestamp);

    return (
        <section className="max-w-7xl mx-auto px-6 py-12 animate-in fade-in duration-500">
            {/* Nav */}
            <button onClick={() => navigate('/')} className="flex items-center gap-2 text-slate-500 hover:text-kingfisher-royal mb-6 transition-colors group">
                <ArrowLeft className="w-5 h-5 group-hover:-translate-x-1 transition-transform" />
                Back to Dashboard
            </button>

            {/* Header / Master Spectrogram */}
            <div className="mb-12">
                <div className="flex flex-col md:flex-row justify-between items-end mb-6 gap-4">
                    <div>
                        <h1 className="text-3xl md:text-4xl font-display font-bold text-kingfisher-midnight">Recording Session</h1>
                        <div className="flex items-center gap-2 text-slate-500 mt-2">
                            <Calendar className="w-4 h-4 text-kingfisher-sky" />
                            <span>{new Date(startTime).toLocaleString()}</span>
                            <span className="mx-2">•</span>
                            <Badge variant="neutral">{sessionDetections.length} Detections</Badge>
                        </div>
                    </div>
                </div>

                <div className="bg-black rounded-xl overflow-hidden shadow-2xl border-4 border-white ring-1 ring-slate-200">
                    <img
                        src={masterImageUrl}
                        alt="Full Session Spectrogram"
                        className="w-full h-auto max-h-[500px] object-contain mx-auto"
                    />
                </div>
            </div>

            {/* Detections Grid */}
            <div className="mb-8">
                <h3 className="text-2xl font-bold text-kingfisher-midnight mb-6 flex items-center gap-2">
                    <Grid className="w-6 h-6 text-kingfisher-royal" />
                    Detected Birds
                </h3>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                    {sessionDetections.map((bird, idx) => (
                        <Card key={bird.id || idx} className="flex flex-col group bg-white hover:border-kingfisher-sky/30 transition-all border-2 border-transparent">
                            <div
                                className="relative aspect-video bg-slate-100 overflow-hidden mb-3 rounded-md cursor-pointer"
                                onClick={() => setSelectedBird(bird)}
                            >
                                <img
                                    src={bird.single_image_url}
                                    alt={bird.species}
                                    className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                                />
                                <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                                    <Maximize2 className="w-6 h-6 text-white drop-shadow-md" />
                                </div>
                                <div className="absolute top-2 right-2">
                                    <Badge variant={bird.confidence > 0.8 ? "success" : "warning"}>
                                        {Math.round(bird.confidence * 100)}%
                                    </Badge>
                                </div>
                            </div>

                            <div className="flex-1">
                                <h5 className="text-lg font-bold text-kingfisher-midnight">{bird.species}</h5>
                                <div className="space-y-1 text-xs text-slate-600 mt-2">
                                    <div className="flex items-center gap-1">
                                        <Calendar className="w-3 h-3 text-kingfisher-sky" />
                                        <span>{new Date(bird.timestamp).toLocaleTimeString()}</span>
                                    </div>
                                </div>
                            </div>

                            <div className="mt-3 pt-3 border-t border-slate-100">
                                <a
                                    href={bird.audio_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex items-center gap-2 text-kingfisher-royal font-bold text-xs hover:underline"
                                >
                                    <Music className="w-3 h-3" />
                                    Listen Segment
                                </a>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>

            {/* ENHANCED Single Bird Modal */}
            {selectedBird && (
                <div className="fixed inset-0 z-[100] flex items-center justify-center bg-black/90 p-4 backdrop-blur-sm" onClick={() => setSelectedBird(null)}>
                    <div className="relative max-w-5xl w-full bg-white rounded-2xl overflow-hidden shadow-2xl flex flex-col md:flex-row max-h-[90vh]" onClick={e => e.stopPropagation()}>

                        {/* LEFT COLUMN: Large Image */}
                        <div className="w-full md:w-2/3 bg-slate-900 flex items-center justify-center p-6 relative overflow-hidden">
                            <img
                                src={selectedBird.single_image_url}
                                alt={selectedBird.species}
                                className="max-w-full max-h-[80vh] object-contain shadow-2xl rounded-lg"
                            />
                            <button
                                onClick={() => setSelectedBird(null)}
                                className="absolute top-4 left-4 p-2 bg-black/50 hover:bg-black/70 text-white rounded-full md:hidden"
                            >
                                <X className="w-6 h-6" />
                            </button>
                        </div>

                        {/* RIGHT COLUMN: Metadata Panel */}
                        <div className="w-full md:w-1/3 bg-white p-8 flex flex-col overflow-y-auto border-l border-slate-100">

                            {/* Close Button (Desktop) */}
                            <div className="hidden md:flex justify-end mb-4">
                                <button onClick={() => setSelectedBird(null)} className="p-2 hover:bg-slate-100 text-slate-400 hover:text-kingfisher-midnight rounded-full transition-colors">
                                    <X className="w-6 h-6" />
                                </button>
                            </div>

                            <div className="flex-1">
                                <div className="mb-6">
                                    <div className="text-sm font-bold text-kingfisher-sky uppercase tracking-wider mb-2">Species Identification</div>
                                    <h2 className="text-3xl font-display font-bold text-kingfisher-midnight leading-tight">{selectedBird.species}</h2>
                                </div>

                                <div className="space-y-6">
                                    {/* Confidence Score */}
                                    <div className="bg-slate-50 p-4 rounded-xl border border-slate-100">
                                        <div className="flex justify-between items-center mb-2">
                                            <span className="text-sm font-medium text-slate-500">Confidence</span>
                                            <span className={`font-bold text-lg ${selectedBird.confidence > 0.8 ? "text-green-600" : "text-amber-600"}`}>
                                                {Math.round(selectedBird.confidence * 100)}%
                                            </span>
                                        </div>
                                        <div className="w-full bg-slate-200 rounded-full h-2">
                                            <div
                                                className={`h-2 rounded-full transition-all duration-1000 ${selectedBird.confidence > 0.8 ? "bg-green-500" : "bg-amber-500"}`}
                                                style={{ width: `${selectedBird.confidence * 100}%` }}
                                            ></div>
                                        </div>
                                    </div>

                                    {/* Timestamp */}
                                    <div>
                                        <h4 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-3">Detection Details</h4>
                                        <div className="flex items-start gap-4 mb-4">
                                            <div className="p-2 bg-blue-50 text-blue-600 rounded-lg">
                                                <Calendar className="w-5 h-5" />
                                            </div>
                                            <div>
                                                <div className="text-sm font-medium text-slate-900">{new Date(selectedBird.timestamp).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}</div>
                                                <div className="text-sm text-slate-500">{new Date(selectedBird.timestamp).toLocaleTimeString()}</div>
                                            </div>
                                        </div>

                                        {/* Location */}
                                        {(selectedBird.lat !== null && selectedBird.lon !== null) ? (
                                            <div className="flex items-start gap-4">
                                                <div className="p-2 bg-red-50 text-red-600 rounded-lg">
                                                    <MapPin className="w-5 h-5" />
                                                </div>
                                                <div>
                                                    <div className="text-sm font-medium text-slate-900">Detected Location</div>
                                                    <div className="text-sm text-slate-500 font-mono text-xs mt-1">
                                                        Lat: {selectedBird.lat.toFixed(6)} <br />
                                                        Lon: {selectedBird.lon.toFixed(6)}
                                                    </div>
                                                </div>
                                            </div>
                                        ) : (
                                            <div className="flex items-start gap-4 opacity-50">
                                                <div className="p-2 bg-slate-50 text-slate-400 rounded-lg">
                                                    <MapPin className="w-5 h-5" />
                                                </div>
                                                <div>
                                                    <div className="text-sm font-medium text-slate-900">Location Unavailable</div>
                                                </div>
                                            </div>
                                        )}
                                    </div>
                                </div>
                            </div>

                            {/* Footer Actions */}
                            <div className="mt-8 pt-6 border-t border-slate-100">
                                <a
                                    href={selectedBird.audio_url}
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    className="flex w-full items-center justify-center gap-2 bg-kingfisher-royal text-white px-6 py-4 rounded-xl font-bold hover:bg-kingfisher-midnight transition-all shadow-lg hover:shadow-xl transform hover:-translate-y-1"
                                >
                                    <Music className="w-5 h-5" />
                                    Play Audio Recording
                                </a>
                                <p className="text-center text-xs text-slate-400 mt-4">
                                    Detection ID: {selectedBird.id}
                                </p>
                            </div>

                        </div>
                    </div>
                </div>
            )}
        </section>
    );
}
