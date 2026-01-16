import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { LucideIcon, Wifi, WifiOff } from 'lucide-react';

interface NavigationItem {
  id: string;
  name: string;
  icon: LucideIcon;
  path: string;
}

interface HeaderProps {
  navigation: NavigationItem[];
  currentPage: string;
  onPageChange: (page: string) => void;
  isOnline: boolean;
}

export const Header: React.FC<HeaderProps> = ({
  navigation,
  currentPage,
  onPageChange,
  isOnline
}) => {
  const location = useLocation();

  return (
    <header className="bg-white shadow-lg border-b border-gray-200">
      <div className="container mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          {/* Logo and Title */}
          <div className="flex items-center space-x-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-saint-blue to-divine-purple rounded-lg flex items-center justify-center">
                <span className="text-white font-bold text-lg">B</span>
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Bible in a Year</h1>
                <p className="text-sm text-gray-600">with AI Spiritual Companions</p>
              </div>
            </div>
          </div>

          {/* Navigation */}
          <nav className="hidden md:flex items-center space-x-1">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.id}
                  to={item.path}
                  onClick={() => onPageChange(item.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-saint-blue to-divine-purple text-white shadow-md'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={18} />
                  <span className="font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>

          {/* Status and Mobile Menu */}
          <div className="flex items-center space-x-4">
            {/* Network Status */}
            <div className={`flex items-center space-x-2 px-3 py-1 rounded-full text-sm ${
              isOnline
                ? 'bg-green-100 text-green-700'
                : 'bg-red-100 text-red-700'
            }`}>
              {isOnline ? <Wifi size={14} /> : <WifiOff size={14} />}
              <span className="hidden sm:inline">
                {isOnline ? 'Online' : 'Offline'}
              </span>
            </div>

            {/* Mobile Navigation Toggle */}
            <button className="md:hidden p-2 rounded-lg hover:bg-gray-100">
              <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
          </div>
        </div>

        {/* Mobile Navigation Menu */}
        <div className="md:hidden mt-4 pt-4 border-t border-gray-200">
          <nav className="grid grid-cols-2 gap-2">
            {navigation.map((item) => {
              const Icon = item.icon;
              const isActive = location.pathname === item.path;

              return (
                <Link
                  key={item.id}
                  to={item.path}
                  onClick={() => onPageChange(item.id)}
                  className={`flex items-center space-x-2 px-3 py-2 rounded-lg transition-all duration-200 ${
                    isActive
                      ? 'bg-gradient-to-r from-saint-blue to-divine-purple text-white shadow-md'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon size={16} />
                  <span className="text-sm font-medium">{item.name}</span>
                </Link>
              );
            })}
          </nav>
        </div>
      </div>
    </header>
  );
};