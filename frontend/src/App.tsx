import { Routes, Route } from 'react-router-dom';
import { Hero } from './components/Hero';
import { BirdGallery } from './components/BirdGallery';
import { SessionDetail } from './components/SessionDetail';

function App() {
  return (
    <div className="min-h-screen bg-slate-50 bg-geometric-pattern">
      <header className="fixed top-0 w-full z-50 bg-white/80 backdrop-blur-md border-b border-slate-100">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="font-display font-bold text-xl text-kingfisher-midnight tracking-tight">
            Project <span className="text-kingfisher-royal">AvianNet</span>
          </div>
          <nav className="hidden md:block">
            <ul className="flex space-x-8 text-sm font-medium text-slate-600">
              <li><a href="/" className="hover:text-kingfisher-royal transition-colors">Dashboard</a></li>
              <li><a href="#" className="hover:text-kingfisher-royal transition-colors">Live Feed</a></li>
              <li><a href="#" className="hover:text-kingfisher-royal transition-colors">Analytics</a></li>
            </ul>
          </nav>
        </div>
      </header>

      <main className="pt-16">
        <Routes>
          <Route path="/" element={
            <>
              <Hero />
              <BirdGallery />
            </>
          } />
          <Route path="/session/:sessionId" element={<SessionDetail />} />
        </Routes>
      </main>

      <footer className="bg-kingfisher-midnight text-white py-12">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h4 className="font-display font-bold text-lg mb-4">About</h4>
            <p className="text-slate-400 text-sm leading-relaxed">
              Advanced acoustic monitoring for biodiversity conservation.
              Powered by BirdNET and React.
            </p>
          </div>
          <div>
            {/* Spacers */}
          </div>
          <div className="text-right">
            <p className="text-slate-500 text-sm">© 2024 Project Kingfisher</p>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;
