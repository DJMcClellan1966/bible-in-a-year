import React, { useState, useEffect } from 'react';
import { DailyReading, DiaryEntry } from '../types';
import { BibleApiService } from '../services/api';
import { Save, BookOpen, MessageSquare, Plus, X } from 'lucide-react';

interface DiaryEditorProps {
  date: string;
  reading: DailyReading | null;
  existingEntry: DiaryEntry | null;
  onSave: () => void;
}

interface MarginNote {
  id: string;
  verse?: string;
  note: string;
  timestamp: string;
  category: 'reflection' | 'question' | 'insight' | 'prayer';
}

export const DiaryEditor: React.FC<DiaryEditorProps> = ({
  date,
  reading,
  existingEntry,
  onSave
}) => {
  const [personalNotes, setPersonalNotes] = useState('');
  const [marginNotes, setMarginNotes] = useState<{ [key: string]: string }>({});
  const [aiInsights, setAiInsights] = useState('');
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    if (existingEntry) {
      setPersonalNotes(existingEntry.personal_notes || '');
      setMarginNotes(existingEntry.margin_notes || {});
      setAiInsights(existingEntry.ai_insights || '');
    } else {
      setPersonalNotes('');
      setMarginNotes({});
      setAiInsights('');
    }
  }, [existingEntry]);

  const handleSave = async () => {
    try {
      setSaving(true);
      await BibleApiService.saveDiaryEntry({
        date,
        reading_passage: reading?.passages.join('; ') || '',
        personal_notes: personalNotes,
        margin_notes: marginNotes,
        ai_insights: aiInsights
      });
      onSave();
    } catch (error) {
      console.error('Failed to save diary entry:', error);
    } finally {
      setSaving(false);
    }
  };

  const addMarginNote = (verse?: string) => {
    const id = `note_${Date.now()}`;
    setMarginNotes(prev => ({
      ...prev,
      [id]: verse ? `Note on ${verse}: ` : ''
    }));
  };

  const updateMarginNote = (id: string, note: string) => {
    setMarginNotes(prev => ({
      ...prev,
      [id]: note
    }));
  };

  const removeMarginNote = (id: string) => {
    setMarginNotes(prev => {
      const updated = { ...prev };
      delete updated[id];
      return updated;
    });
  };

  const getCategoryColor = (category: string) => {
    switch (category) {
      case 'reflection': return 'bg-blue-100 border-blue-300 text-blue-800';
      case 'question': return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      case 'insight': return 'bg-green-100 border-green-300 text-green-800';
      case 'prayer': return 'bg-purple-100 border-purple-300 text-purple-800';
      default: return 'bg-gray-100 border-gray-300 text-gray-800';
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          <BookOpen className="text-saint-blue" size={20} />
          <h3 className="text-lg font-semibold text-gray-900">Personal Diary</h3>
          <span className="text-sm text-gray-600">
            {new Date(date).toLocaleDateString('en-US', {
              weekday: 'long',
              year: 'numeric',
              month: 'long',
              day: 'numeric'
            })}
          </span>
        </div>

        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center space-x-2 px-4 py-2 bg-gradient-to-r from-saint-blue to-divine-purple text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors disabled:opacity-50"
        >
          <Save size={18} />
          <span>{saving ? 'Saving...' : 'Save Entry'}</span>
        </button>
      </div>

      {/* Today's Reading Reference */}
      {reading && (
        <div className="grace-card">
          <h4 className="font-medium text-gray-900 mb-2">Today's Reading</h4>
          <p className="text-gray-700 bible-text">
            {reading.passages.join(', ')}
          </p>
          {reading.theme && (
            <p className="text-saint-blue text-sm mt-1 italic">
              Theme: {reading.theme}
            </p>
          )}
        </div>
      )}

      {/* Personal Notes */}
      <div className="grace-card">
        <div className="flex items-center space-x-2 mb-4">
          <MessageSquare className="text-saint-blue" size={18} />
          <h4 className="font-medium text-gray-900">Personal Reflections</h4>
        </div>

        <textarea
          value={personalNotes}
          onChange={(e) => setPersonalNotes(e.target.value)}
          placeholder="Write your personal thoughts, reflections, and insights about today's reading..."
          className="w-full h-32 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saint-blue focus:border-transparent resize-vertical"
          rows={6}
        />

        <div className="flex justify-between items-center mt-2 text-sm text-gray-600">
          <span>{personalNotes.length} characters</span>
          <button
            onClick={() => addMarginNote()}
            className="flex items-center space-x-1 text-saint-blue hover:text-blue-700 transition-colors"
          >
            <Plus size={14} />
            <span>Add margin note</span>
          </button>
        </div>
      </div>

      {/* Margin Notes */}
      {Object.keys(marginNotes).length > 0 && (
        <div className="grace-card">
          <h4 className="font-medium text-gray-900 mb-4">Margin Notes</h4>

          <div className="space-y-3">
            {Object.entries(marginNotes).map(([id, note]) => (
              <div key={id} className="margin-note">
                <div className="flex items-start justify-between mb-2">
                  <div className="flex-1">
                    <textarea
                      value={note}
                      onChange={(e) => updateMarginNote(id, e.target.value)}
                      placeholder="Write your margin note here..."
                      className="w-full p-2 bg-transparent border-none resize-none focus:outline-none text-sm"
                      rows={2}
                    />
                  </div>
                  <button
                    onClick={() => removeMarginNote(id)}
                    className="ml-2 text-gray-400 hover:text-red-500 transition-colors"
                  >
                    <X size={14} />
                  </button>
                </div>
                <div className="text-xs text-gray-500">
                  Margin note • {new Date().toLocaleDateString()}
                </div>
              </div>
            ))}
          </div>

          <button
            onClick={() => addMarginNote()}
            className="mt-3 flex items-center space-x-1 text-saint-blue hover:text-blue-700 transition-colors text-sm"
          >
            <Plus size={14} />
            <span>Add another margin note</span>
          </button>
        </div>
      )}

      {/* AI Insights */}
      <div className="grace-card">
        <h4 className="font-medium text-gray-900 mb-4">AI-Generated Insights</h4>

        <textarea
          value={aiInsights}
          onChange={(e) => setAiInsights(e.target.value)}
          placeholder="Space for AI-generated insights, or your own additional reflections..."
          className="w-full h-24 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-divine-purple focus:border-transparent resize-vertical"
          rows={4}
        />

        <div className="flex justify-between items-center mt-2 text-sm text-gray-600">
          <span>This can be populated by AI commentary or your own insights</span>
          <span>{aiInsights.length} characters</span>
        </div>
      </div>

      {/* Save Reminder */}
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
        <div className="flex items-center space-x-2">
          <div className="w-2 h-2 bg-yellow-400 rounded-full"></div>
          <p className="text-sm text-yellow-800">
            <strong>Remember to save:</strong> Your diary entries are saved locally and will persist between sessions.
            Don't forget to save your thoughts before navigating away!
          </p>
        </div>
      </div>
    </div>
  );
};