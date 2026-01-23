import { Bird, Activity } from 'lucide-react';
import { Button } from './ui/Button';
import { Link } from 'react-router-dom';

export function Hero() {
    return (
        <section className="relative w-full min-h-[70vh] flex items-center justify-center overflow-hidden bg-coastal-blue">
            {/* Wave Pattern Bottom */}
            <div className="absolute bottom-0 left-0 right-0 h-24 bg-no-repeat bg-cover bg-bottom"
                style={{
                    backgroundImage: `url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1440 100'%3E%3Cpath fill='%23FFF8E7' d='M0,64L80,58.7C160,53,320,43,480,48C640,53,800,75,960,74.7C1120,75,1280,53,1360,42.7L1440,32L1440,100L1360,100C1280,100,1120,100,960,100C800,100,640,100,480,100C320,100,160,100,80,100L0,100Z'%3E%3C/path%3E%3C/svg%3E")`
                }}
            />

            {/* Decorative Birds */}
            <div className="absolute top-20 left-10 text-white/20">
                <Bird className="w-32 h-32 rotate-12" />
            </div>
            <div className="absolute top-40 right-20 text-white/15">
                <Bird className="w-24 h-24 -rotate-12 scale-x-[-1]" />
            </div>
            <div className="absolute bottom-32 left-1/4 text-white/10">
                <Bird className="w-16 h-16 rotate-6" />
            </div>

            <div className="relative z-10 max-w-5xl mx-auto px-6 text-center">
                {/* Main Title - Poster Style */}
                <div className="mb-8">
                    <div className="inline-block bg-sand-light border-4 border-ink-black rounded-2xl shadow-brutal-xl px-8 py-6 mb-6">
                        <h1 className="text-5xl md:text-7xl lg:text-8xl font-display font-bold tracking-tight text-ink-black leading-none">
                            <span className="text-coastal-blue">AVIAN</span>NET
                        </h1>
                    </div>
                </div>

                <p className="text-xl md:text-2xl text-white/90 mb-10 max-w-2xl mx-auto font-body leading-relaxed">
                    Real-time acoustic bird monitoring powered by
                    <span className="font-bold text-sun-yellow"> AI classification</span>
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                    <Button size="lg" onClick={() => document.getElementById('gallery')?.scrollIntoView({ behavior: 'smooth' })}>
                        <Activity className="w-5 h-5" />
                        View Detections
                    </Button>
                    <Link to="/analytics">
                        <Button variant="outline" size="lg" className="bg-white text-ink-black hover:bg-sun-yellow hover:text-ink-black">
                            <Bird className="w-5 h-5" />
                            Analytics
                        </Button>
                    </Link>
                </div>

                {/* Stats Banner */}
                <div className="mt-12 flex flex-wrap justify-center gap-6">
                    <div className="bg-white/20 backdrop-blur-sm border-2 border-white/30 rounded-xl px-6 py-3">
                        <span className="text-3xl font-display font-bold text-sun-yellow">AI</span>
                        <span className="text-sm text-white/80 ml-2">Powered</span>
                    </div>
                    <div className="bg-white/20 backdrop-blur-sm border-2 border-white/30 rounded-xl px-6 py-3">
                        <span className="text-3xl font-display font-bold text-sun-yellow">24/7</span>
                        <span className="text-sm text-white/80 ml-2">Monitoring</span>
                    </div>
                    <div className="bg-white/20 backdrop-blur-sm border-2 border-white/30 rounded-xl px-6 py-3">
                        <span className="text-3xl font-display font-bold text-sun-yellow">Real</span>
                        <span className="text-sm text-white/80 ml-2">Time</span>
                    </div>
                </div>
            </div>
        </section>
    );
}
