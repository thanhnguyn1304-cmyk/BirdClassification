import { Routes, Route, Link } from 'react-router-dom';
import { Bird, Bell } from 'lucide-react';
import { Hero } from './components/Hero';
import { BirdGallery } from './components/BirdGallery';
import { SessionDetail } from './components/SessionDetail';
import { Analytics } from './components/Analytics';
import { NotificationProvider, useNotifications } from './contexts/NotificationContext';
import { ToastContainer } from './components/Toast';

function AppContent() {
  const { unreadCount, markAllAsRead } = useNotifications();

  return (
    <div className="min-h-screen bg-coastal-blue">
      {/* Header - Brutal Style */}
      <header className="fixed top-0 w-full z-50 bg-sand-light border-b-4 border-ink-black">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link to="/" className="flex items-center gap-2 font-display font-bold text-xl text-ink-black tracking-tighter uppercase">
            <Bird className="w-6 h-6 text-coastal-blue" />
            <span><span className="text-coastal-blue">Avian</span>Net</span>
          </Link>
          <nav className="flex items-center gap-4">
            <ul className="flex space-x-2 text-sm font-bold">
              <li>
                <Link to="/" className="px-4 py-2 rounded-lg border-2 border-transparent hover:border-ink-black hover:bg-sun-yellow transition-all">
                  Dashboard
                </Link>
              </li>
              <li>
                <Link to="/analytics" className="px-4 py-2 rounded-lg border-2 border-transparent hover:border-ink-black hover:bg-sun-yellow transition-all">
                  Analytics
                </Link>
              </li>
            </ul>

            {/* Notification Bell */}
            <button
              onClick={markAllAsRead}
              className="relative p-2 rounded-lg hover:bg-sun-yellow border-2 border-transparent hover:border-ink-black transition-all group"
            >
              <Bell className="w-6 h-6 text-ink-black" />
              {unreadCount > 0 && (
                <span className="absolute -top-1 -right-1 flex h-5 w-5 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white border-2 border-white">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>
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
          <Route path="/analytics" element={<Analytics />} />
        </Routes>
      </main>

      {/* Footer - Brutal Style */}
      <footer className="bg-ink-black text-white py-12 border-t-4 border-sun-yellow">
        <div className="max-w-7xl mx-auto px-6 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div>
            <h4 className="font-display font-bold text-2xl mb-4 text-sun-yellow">About</h4>
            <p className="text-white/70 text-sm leading-relaxed font-body">
              Advanced acoustic monitoring for biodiversity conservation.
              Powered by BirdNET AI and React.
            </p>
          </div>
          <div className="flex items-center justify-center">
            <Bird className="w-20 h-20 text-white/20" />
          </div>
          <div className="text-right">
            <p className="text-white/50 text-sm font-body">© 2024 Project AvianNet</p>
            <p className="text-sun-yellow font-display text-lg mt-2">🐦 San Sebastian Theme</p>
          </div>
        </div>
      </footer>

      {/* Toast Container for Popups */}
      <ToastContainer />
    </div>
  );
}

function App() {
  return (
    <NotificationProvider>
      <AppContent />
    </NotificationProvider>
  );
}

export default App;
