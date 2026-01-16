import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { Header } from './components/Header';
import { Footer } from './components/Footer';
import { DailyReading } from './pages/DailyReading';
import { Diary } from './pages/Diary';
import { AIHelpers } from './pages/AIHelpers';
import { Progress } from './pages/Progress';
import { Settings } from './pages/Settings';
import { NetworkMonitor } from './services/api';
import { BookOpen, BookMarked, Users, BarChart3, Settings as SettingsIcon } from 'lucide-react';

function App() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [currentPage, setCurrentPage] = useState('reading');

  useEffect(() => {
    const handleOnlineStatus = (online: boolean) => {
      setIsOnline(online);
    };

    NetworkMonitor.addListener(handleOnlineStatus);

    return () => {
      NetworkMonitor.removeListener(handleOnlineStatus);
    };
  }, []);

  const navigation = [
    { id: 'reading', name: 'Daily Reading', icon: BookOpen, path: '/' },
    { id: 'diary', name: 'My Diary', icon: BookMarked, path: '/diary' },
    { id: 'helpers', name: 'AI Helpers', icon: Users, path: '/helpers' },
    { id: 'progress', name: 'Progress', icon: BarChart3, path: '/progress' },
    { id: 'settings', name: 'Settings', icon: SettingsIcon, path: '/settings' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-purple-50">
      <Header
        navigation={navigation}
        currentPage={currentPage}
        onPageChange={setCurrentPage}
        isOnline={isOnline}
      />

      <main className="container mx-auto px-4 py-8 max-w-4xl">
        <Routes>
          <Route path="/" element={<DailyReading />} />
          <Route path="/diary" element={<Diary />} />
          <Route path="/helpers" element={<AIHelpers />} />
          <Route path="/progress" element={<Progress />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>

      <Footer />

      {/* Offline indicator */}
      {!isOnline && (
        <div className="fixed bottom-4 right-4 bg-red-500 text-white px-4 py-2 rounded-lg shadow-lg">
          <div className="flex items-center space-x-2">
            <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
            <span className="text-sm font-medium">Offline Mode</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default App;