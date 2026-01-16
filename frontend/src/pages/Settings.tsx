import React, { useState } from 'react';
import { Settings as SettingsIcon, Moon, Sun, Monitor, Type, Volume2 } from 'lucide-react';

export const Settings: React.FC = () => {
  const [theme, setTheme] = useState<'light' | 'dark' | 'auto'>('auto');
  const [fontSize, setFontSize] = useState<'small' | 'medium' | 'large'>('medium');
  const [notifications, setNotifications] = useState(true);
  const [offlineMode, setOfflineMode] = useState(false);

  const themeOptions = [
    { value: 'light', label: 'Light', icon: Sun },
    { value: 'dark', label: 'Dark', icon: Moon },
    { value: 'auto', label: 'Auto', icon: Monitor },
  ];

  const fontSizeOptions = [
    { value: 'small', label: 'Small' },
    { value: 'medium', label: 'Medium' },
    { value: 'large', label: 'Large' },
  ];

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto bg-gradient-to-r from-saint-blue to-divine-purple rounded-full flex items-center justify-center mb-4">
          <SettingsIcon size={32} className="text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Settings</h2>
        <p className="text-gray-600 mt-2">
          Customize your Bible reading experience
        </p>
      </div>

      {/* Appearance Settings */}
      <div className="grace-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Appearance</h3>

        <div className="space-y-6">
          {/* Theme */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Theme
            </label>
            <div className="grid grid-cols-3 gap-3">
              {themeOptions.map((option) => {
                const Icon = option.icon;
                return (
                  <button
                    key={option.value}
                    onClick={() => setTheme(option.value as any)}
                    className={`p-3 rounded-lg border-2 transition-all ${
                      theme === option.value
                        ? 'border-saint-blue bg-blue-50 text-saint-blue'
                        : 'border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <Icon size={20} className="mx-auto mb-2" />
                    <div className="text-sm font-medium">{option.label}</div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Font Size */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">
              Font Size
            </label>
            <div className="grid grid-cols-3 gap-3">
              {fontSizeOptions.map((option) => (
                <button
                  key={option.value}
                  onClick={() => setFontSize(option.value as any)}
                  className={`p-3 rounded-lg border-2 transition-all ${
                    fontSize === option.value
                      ? 'border-saint-blue bg-blue-50 text-saint-blue'
                      : 'border-gray-200 hover:border-gray-300'
                  }`}
                >
                  <Type size={20} className="mx-auto mb-2" />
                  <div className="text-sm font-medium">{option.label}</div>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* App Preferences */}
      <div className="grace-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">App Preferences</h3>

        <div className="space-y-4">
          {/* Notifications */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <Volume2 size={20} className="text-gray-500" />
              <div>
                <div className="font-medium text-gray-900">Notifications</div>
                <div className="text-sm text-gray-600">
                  Receive reminders for daily readings
                </div>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={notifications}
                onChange={(e) => setNotifications(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-saint-blue/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-saint-blue"></div>
            </label>
          </div>

          {/* Offline Mode */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="w-5 h-5 bg-gray-300 rounded"></div>
              <div>
                <div className="font-medium text-gray-900">Offline Mode</div>
                <div className="text-sm text-gray-600">
                  Prioritize offline functionality and local storage
                </div>
              </div>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={offlineMode}
                onChange={(e) => setOfflineMode(e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-saint-blue/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-saint-blue"></div>
            </label>
          </div>
        </div>
      </div>

      {/* Data Management */}
      <div className="grace-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Data Management</h3>

        <div className="space-y-3">
          <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
            <div className="font-medium text-gray-900">Export Diary Entries</div>
            <div className="text-sm text-gray-600">Download all your diary entries as JSON</div>
          </button>

          <button className="w-full text-left px-4 py-3 bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors">
            <div className="font-medium text-gray-900">Clear Cache</div>
            <div className="text-sm text-gray-600">Clear cached Bible text and AI responses</div>
          </button>

          <button className="w-full text-left px-4 py-3 bg-red-50 hover:bg-red-100 rounded-lg transition-colors">
            <div className="font-medium text-red-900">Reset All Data</div>
            <div className="text-sm text-red-600">Permanently delete all diary entries and settings</div>
          </button>
        </div>
      </div>

      {/* About */}
      <div className="grace-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">About</h3>

        <div className="space-y-3 text-sm text-gray-600">
          <p>
            <strong>Bible in a Year with AI Helpers</strong> v1.0.0
          </p>
          <p>
            Experience Scripture with spiritual guidance from Saints Augustine and Aquinas,
            powered by AI and made possible by classic Christian texts.
          </p>
          <p>
            Built with React, FastAPI, and love for spiritual growth.
          </p>
        </div>
      </div>
    </div>
  );
};