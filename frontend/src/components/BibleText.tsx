import React, { useState } from 'react';
import { DailyReading } from '../types';
import { BookOpen, Eye, EyeOff } from 'lucide-react';

interface BibleTextProps {
  reading: DailyReading;
}

export const BibleText: React.FC<BibleTextProps> = ({ reading }) => {
  const [expandedPassages, setExpandedPassages] = useState<Set<string>>(new Set());

  const togglePassage = (passage: string) => {
    const newExpanded = new Set(expandedPassages);
    if (newExpanded.has(passage)) {
      newExpanded.delete(passage);
    } else {
      newExpanded.add(passage);
    }
    setExpandedPassages(newExpanded);
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center space-x-2 mb-4">
        <BookOpen className="text-saint-blue" size={20} />
        <h3 className="text-lg font-semibold text-gray-900">Today's Reading</h3>
        {reading.total_verses && (
          <span className="text-sm text-gray-600">
            ({reading.total_verses} verses)
          </span>
        )}
      </div>

      <div className="space-y-4">
        {reading.passages.map((passage, index) => {
          const isExpanded = expandedPassages.has(passage);
          const textData = reading.text?.[passage];

          return (
            <div key={index} className="border border-gray-200 rounded-lg overflow-hidden">
              {/* Passage Header */}
              <div
                className="bg-gray-50 px-4 py-3 cursor-pointer hover:bg-gray-100 transition-colors"
                onClick={() => togglePassage(passage)}
              >
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-gray-900 bible-text">
                    {passage}
                  </h4>
                  <div className="flex items-center space-x-2">
                    {textData?.citation && (
                      <span className="text-xs text-gray-600">
                        {textData.citation}
                      </span>
                    )}
                    {isExpanded ? (
                      <EyeOff size={16} className="text-gray-500" />
                    ) : (
                      <Eye size={16} className="text-gray-500" />
                    )}
                  </div>
                </div>
              </div>

              {/* Passage Content */}
              {isExpanded && (
                <div className="p-4 bg-white">
                  {textData ? (
                    <div className="space-y-3">
                      {Object.entries(textData.text).map(([verse, text]) => (
                        <div key={verse} className="flex space-x-3">
                          <span className="text-saint-blue font-medium text-sm min-w-[1.5rem]">
                            {verse}
                          </span>
                          <p className="bible-text text-gray-800 leading-relaxed flex-1">
                            {text}
                          </p>
                        </div>
                      ))}
                      {textData.note && (
                        <div className="mt-4 p-3 bg-blue-50 border-l-4 border-saint-blue rounded">
                          <p className="text-sm text-blue-800 italic">
                            {textData.note}
                          </p>
                        </div>
                      )}
                    </div>
                  ) : (
                    <div className="text-center py-8 text-gray-500">
                      <BookOpen size={32} className="mx-auto mb-3 opacity-50" />
                      <p className="text-sm">
                        Full text for {passage} will be available when online or with complete Bible database.
                      </p>
                      <p className="text-xs mt-2 text-gray-400">
                        This is a demo version. Complete Bible integration coming soon.
                      </p>
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Reading Summary */}
      <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg border border-gray-200">
        <h4 className="font-medium text-gray-900 mb-2">Reading Summary</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Passages:</span>
            <span className="ml-2 font-medium">{reading.passages.length}</span>
          </div>
          <div>
            <span className="text-gray-600">Theme:</span>
            <span className="ml-2 font-medium">{reading.theme || 'Daily Bread'}</span>
          </div>
          <div>
            <span className="text-gray-600">Date:</span>
            <span className="ml-2 font-medium">{reading.date}</span>
          </div>
        </div>
      </div>
    </div>
  );
};