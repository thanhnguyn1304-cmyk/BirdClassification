import { MousePointer2, Activity } from 'lucide-react';
import { Button } from './ui/Button';

export function Hero() {
    return (
        <section className="relative w-full min-h-[60vh] flex items-center justify-center overflow-hidden bg-white/50 backdrop-blur-sm border-b-2 border-red-500">
            {/* Added border for visibility check */}

            {/* Background Geometric Elements */}
            <div className="absolute inset-0 pointer-events-none overflow-hidden">
                <div className="absolute -top-20 -right-20 w-96 h-96 bg-kingfisher-sky/10 rounded-full blur-3xl" />
                <div className="absolute top-40 -left-20 w-72 h-72 bg-kingfisher-royal/5 rounded-full blur-3xl opacity-60" />

                <div
                    className="absolute top-10 right-10 w-32 h-32 bg-kingfisher-turquoise/20"
                    style={{ clipPath: 'polygon(20% 0%, 80% 0%, 100% 100%, 0% 100%)' }}
                />
                <div
                    className="absolute bottom-20 left-10 w-24 h-24 bg-kingfisher-coral/20"
                    style={{ clipPath: 'polygon(50% 0%, 0% 100%, 100% 100%)' }}
                />
            </div>

            <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
                <div className="opacity-100">
                    <h1 className="text-6xl md:text-8xl font-display font-bold mb-6 tracking-tight text-kingfisher-midnight">
                        <span className="text-blue-600">
                            Project
                        </span>{" "}
                        AvianNet
                    </h1>

                    <p className="text-xl md:text-2xl text-slate-600 mb-10 max-w-2xl mx-auto font-light leading-relaxed">
                        Real-time avian acoustic monitoring and classification visualized through a
                        <span className="font-semibold text-kingfisher-royal"> sharp, geometric lens.</span>
                    </p>

                    <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                        <Button size="lg" onClick={() => document.getElementById('gallery')?.scrollIntoView({ behavior: 'smooth' })}>
                            <Activity className="w-5 h-5 mr-2" />
                            View Detections
                        </Button>
                        <Button variant="outline" size="lg">
                            <MousePointer2 className="w-5 h-5 mr-2" />
                            Learn More
                        </Button>
                    </div>
                </div>
            </div>
        </section>
    );
}
