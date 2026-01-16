import React, { useState, useEffect } from 'react';
import { format, subDays, addDays } from 'date-fns';
import { Calendar, BookOpen, MessageSquare, Search } from 'lucide-react';
import { BibleApiService } from '../services/api';
import { DiaryEntry } from '../types';

export const Diary: React.FC = () => {
  const [entries, setEntries] = useState<{ [date: string]: DiaryEntry }>({});
  const [selectedDate, setSelectedDate] = useState(new Date());
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');

  useEffect(() => {
    loadDiaryEntries();
  }, []);

  const loadDiaryEntries = async () => {
    setLoading(true);
    try {
      // Load entries for the past 30 days
      const dates = [];
      for (let i = 0; i < 30; i++) {
        dates.push(subDays(new Date(), i));
      }

      const entriesData: { [date: string]: DiaryEntry } = {};

      for (const date of dates) {
        const dateStr = format(date, 'yyyy-MM-dd');
        try {
          const entry = await BibleApiService.getDiaryEntry(dateStr);
          if (entry) {
            entriesData[dateStr] = entry;
          }
        } catch (error) {
          // Skip missing entries
        }
      }

      setEntries(entriesData);
    } catch (error) {
      console.error('Failed to load diary entries:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredEntries = Object.entries(entries).filter(([date, entry]) => {
    if (!searchTerm) return true;

    const searchLower = searchTerm.toLowerCase();
    return (
      entry.personal_notes?.toLowerCase().includes(searchLower) ||
      entry.reading_passage?.toLowerCase().includes(searchLower) ||
      entry.ai_insights?.toLowerCase().includes(searchLower) ||
      Object.values(entry.margin_notes || {}).some(note =>
        note.toLowerCase().includes(searchLower)
      )
    );
  });

  const selectedDateStr = format(selectedDate, 'yyyy-MM-dd');
  const selectedEntry = entries[selectedDateStr];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <BookOpen className="text-saint-blue" size={24} />
          <h2 className="text-2xl font-bold text-gray-900">My Spiritual Diary</h2>
        </div>

        <button
          onClick={loadDiaryEntries}
          className="px-4 py-2 bg-saint-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
          disabled={loading}
        >
          {loading ? 'Loading...' : 'Refresh'}
        </button>
      </div>

      {/* Search */}
      <div className="grace-card">
        <div className="relative">
          <Search className="absolute left-3 top-3 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Search your diary entries..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saint-blue focus:border-transparent"
          />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Calendar/Entry List */}
        <div className="lg:col-span-1">
          <div className="grace-card">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Diary Entries</h3>

            {loading ? (
              <div className="flex items-center justify-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-saint-blue"></div>
              </div>
            ) : filteredEntries.length === 0 ? (
              <div className="text-center py-8 text-gray-500">
                <BookOpen size={32} className="mx-auto mb-3 opacity-50" />
                <p>No diary entries found</p>
                {searchTerm && (
                  <p className="text-sm mt-1">Try adjusting your search terms</p>
                )}
              </div>
            ) : (
              <div className="space-y-2 max-h-96 overflow-y-auto">
                {filteredEntries.map(([date, entry]) => (
                  <div
                    key={date}
                    onClick={() => setSelectedDate(new Date(date))}
                    className={`p-3 rounded-lg cursor-pointer transition-colors ${
                      date === selectedDateStr
                        ? 'bg-saint-blue text-white'
                        : 'hover:bg-gray-50'
                    }`}
                  >
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="font-medium">
                          {format(new Date(date), 'MMM d, yyyy')}
                        </div>
                        <div className={`text-sm ${date === selectedDateStr ? 'text-blue-100' : 'text-gray-600'}`}>
                          {entry.reading_passage?.split(';')[0]}
                        </div>
                      </div>
                      <div className="flex space-x-1">
                        {entry.personal_notes && <MessageSquare size={14} />}
                        {(entry.margin_notes && Object.keys(entry.margin_notes).length > 0) && (
                          <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Selected Entry Detail */}
        <div className="lg:col-span-2">
          <div className="grace-card">
            {selectedEntry ? (
              <div className="space-y-6">
                <div className="flex items-center space-x-2">
                  <Calendar className="text-saint-blue" size={20} />
                  <h3 className="text-xl font-semibold text-gray-900">
                    {format(selectedDate, 'EEEE, MMMM d, yyyy')}
                  </h3>
                </div>

                {/* Reading Reference */}
                <div>
                  <h4 className="font-medium text-gray-900 mb-2">Reading</h4>
                  <p className="text-gray-700 bible-text">
                    {selectedEntry.reading_passage}
                  </p>
                </div>

                {/* Personal Notes */}
                {selectedEntry.personal_notes && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2 flex items-center space-x-2">
                      <MessageSquare size={18} />
                      <span>Personal Reflections</span>
                    </h4>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <p className="text-gray-800 whitespace-pre-wrap">
                        {selectedEntry.personal_notes}
                      </p>
                    </div>
                  </div>
                )}

                {/* Margin Notes */}
                {selectedEntry.margin_notes && Object.keys(selectedEntry.margin_notes).length > 0 && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">Margin Notes</h4>
                    <div className="space-y-3">
                      {Object.entries(selectedEntry.margin_notes).map(([id, note]) => (
                        <div key={id} className="margin-note">
                          <p className="text-sm">{note}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* AI Insights */}
                {selectedEntry.ai_insights && (
                  <div>
                    <h4 className="font-medium text-gray-900 mb-2">AI Insights</h4>
                    <div className="bg-purple-50 p-4 rounded-lg border-l-4 border-divine-purple">
                      <p className="text-purple-800 whitespace-pre-wrap">
                        {selectedEntry.ai_insights}
                      </p>
                    </div>
                  </div>
                )}

                {/* Metadata */}
                <div className="text-xs text-gray-500 pt-4 border-t border-gray-200">
                  Created: {selectedEntry.created_at ? new Date(selectedEntry.created_at).toLocaleString() : 'Unknown'}
                  {selectedEntry.updated_at && selectedEntry.updated_at !== selectedEntry.created_at && (
                    <> • Updated: {new Date(selectedEntry.updated_at).toLocaleString()}</>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <BookOpen size={48} className="mx-auto mb-4 opacity-50 text-gray-400" />
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No Entry for {format(selectedDate, 'MMMM d, yyyy')}
                </h3>
                <p className="text-gray-600">
                  Select a date with an entry from the list, or navigate to the Daily Reading page to create one.
                </p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};