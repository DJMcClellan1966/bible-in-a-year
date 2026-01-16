import React, { useState, useEffect } from 'react';
import { format, addDays, subDays } from 'date-fns';
import {
  ChevronLeft,
  ChevronRight,
  BookOpen,
  Users,
  MessageCircle,
  Save,
  Calendar
} from 'lucide-react';
import { BibleApiService } from '../services/api';
import { DailyReading as DailyReadingType, CommentaryResponse, DiaryEntry } from '../types';
import { BibleText } from '../components/BibleText';
import { AICommentary } from '../components/AICommentary';
import { DiaryEditor } from '../components/DiaryEditor';

export const DailyReading: React.FC = () => {
  const [currentDate, setCurrentDate] = useState(new Date());
  const [reading, setReading] = useState<DailyReadingType | null>(null);
  const [diaryEntry, setDiaryEntry] = useState<DiaryEntry | null>(null);
  const [commentary, setCommentary] = useState<CommentaryResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'reading' | 'commentary' | 'diary'>('reading');

  const formattedDate = format(currentDate, 'yyyy-MM-dd');
  const displayDate = format(currentDate, 'EEEE, MMMM d, yyyy');

  useEffect(() => {
    loadDailyReading();
    loadDiaryEntry();
  }, [currentDate]);

  const loadDailyReading = async () => {
    try {
      setLoading(true);
      const data = await BibleApiService.getDailyReading(formattedDate);
      setReading(data);
    } catch (error) {
      console.error('Failed to load daily reading:', error);
      // For demo purposes, show a placeholder
      setReading({
        date: formattedDate,
        passages: ['Coming Soon - Full Bible text integration in progress'],
        theme: 'Daily Spiritual Nourishment'
      });
    } finally {
      setLoading(false);
    }
  };

  const loadDiaryEntry = async () => {
    try {
      const entry = await BibleApiService.getDiaryEntry(formattedDate);
      setDiaryEntry(entry);
    } catch (error) {
      console.error('Failed to load diary entry:', error);
    }
  };

  const handlePreviousDay = () => {
    setCurrentDate(prev => subDays(prev, 1));
    setCommentary(null);
  };

  const handleNextDay = () => {
    setCurrentDate(prev => addDays(prev, 1));
    setCommentary(null);
  };

  const handleGetCommentary = async (helper: string = 'augustine') => {
    if (!reading) return;

    try {
      setLoading(true);
      const response = await BibleApiService.getCommentary({
        passage: reading.passages.join('; '),
        helper: helper,
        personalized: true
      });
      setCommentary(response);
      setActiveTab('commentary');
    } catch (error) {
      console.error('Failed to get commentary:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'reading', label: 'Reading', icon: BookOpen },
    { id: 'commentary', label: 'AI Commentary', icon: Users },
    { id: 'diary', label: 'My Diary', icon: MessageCircle },
  ];

  return (
    <div className="space-y-6">
      {/* Date Navigation */}
      <div className="grace-card">
        <div className="flex items-center justify-between mb-4">
          <button
            onClick={handlePreviousDay}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <ChevronLeft size={20} />
            <span>Previous</span>
          </button>

          <div className="text-center">
            <h2 className="text-2xl font-bold text-gray-900 flex items-center justify-center space-x-2">
              <Calendar size={24} className="text-saint-blue" />
              <span>{displayDate}</span>
            </h2>
            {reading?.theme && (
              <p className="text-saint-blue font-medium mt-1">{reading.theme}</p>
            )}
          </div>

          <button
            onClick={handleNextDay}
            className="flex items-center space-x-2 px-4 py-2 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <span>Next</span>
            <ChevronRight size={20} />
          </button>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="grace-card">
        <div className="flex space-x-1 mb-4">
          {tabs.map((tab) => {
            const Icon = tab.icon;
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as any)}
                className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${
                  activeTab === tab.id
                    ? 'bg-gradient-to-r from-saint-blue to-divine-purple text-white shadow-md'
                    : 'text-gray-700 hover:bg-gray-100'
                }`}
              >
                <Icon size={18} />
                <span>{tab.label}</span>
              </button>
            );
          })}
        </div>

        {/* Tab Content */}
        <div className="min-h-[400px]">
          {activeTab === 'reading' && (
            <div className="space-y-6">
              {loading ? (
                <div className="flex items-center justify-center py-12">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-saint-blue"></div>
                </div>
              ) : reading ? (
                <>
                  <BibleText reading={reading} />

                  {/* AI Helper Actions */}
                  <div className="flex flex-wrap gap-3 pt-4 border-t border-gray-200">
                    <button
                      onClick={() => handleGetCommentary('augustine')}
                      className="flex items-center space-x-2 px-4 py-2 bg-saint-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
                      disabled={loading}
                    >
                      <Users size={18} />
                      <span>Ask Augustine</span>
                    </button>

                    <button
                      onClick={() => handleGetCommentary('aquinas')}
                      className="flex items-center space-x-2 px-4 py-2 bg-divine-purple text-white rounded-lg hover:bg-purple-700 transition-colors"
                      disabled={loading}
                    >
                      <Users size={18} />
                      <span>Ask Aquinas</span>
                    </button>

                    <button
                      onClick={() => handleGetCommentary('combined')}
                      className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-saint-blue to-divine-purple text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors"
                      disabled={loading}
                    >
                      <Users size={18} />
                      <span>Combined Wisdom</span>
                    </button>
                  </div>
                </>
              ) : (
                <div className="text-center py-12 text-gray-500">
                  <BookOpen size={48} className="mx-auto mb-4 opacity-50" />
                  <p>No reading available for this date.</p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'commentary' && (
            <AICommentary
              commentary={commentary}
              onRequestCommentary={handleGetCommentary}
              loading={loading}
            />
          )}

          {activeTab === 'diary' && (
            <DiaryEditor
              date={formattedDate}
              reading={reading}
              existingEntry={diaryEntry}
              onSave={loadDiaryEntry}
            />
          )}
        </div>
      </div>
    </div>
  );
};