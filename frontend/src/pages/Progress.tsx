import React, { useState, useEffect } from 'react';
import { BarChart3, Calendar, BookOpen, TrendingUp } from 'lucide-react';
import { BibleApiService } from '../services/api';
import { ReadingProgress } from '../types';

export const Progress: React.FC = () => {
  const [progress, setProgress] = useState<ReadingProgress | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadProgress();
  }, []);

  const loadProgress = async () => {
    try {
      const data = await BibleApiService.getReadingProgress();
      setProgress(data);
    } catch (error) {
      console.error('Failed to load progress:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-saint-blue"></div>
      </div>
    );
  }

  const completionPercentage = progress?.completion_percentage || 0;
  const daysCompleted = progress?.completed_readings || 0;
  const totalDays = progress?.total_readings || 365;

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto bg-gradient-to-r from-saint-blue to-divine-purple rounded-full flex items-center justify-center mb-4">
          <BarChart3 size={32} className="text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">Reading Progress</h2>
        <p className="text-gray-600 mt-2">
          Track your journey through the Bible in a Year
        </p>
      </div>

      {/* Progress Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="grace-card text-center">
          <div className="w-12 h-12 mx-auto bg-saint-blue rounded-full flex items-center justify-center mb-3">
            <BookOpen size={24} className="text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{daysCompleted}</div>
          <div className="text-gray-600">Days Completed</div>
        </div>

        <div className="grace-card text-center">
          <div className="w-12 h-12 mx-auto bg-divine-purple rounded-full flex items-center justify-center mb-3">
            <Calendar size={24} className="text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{totalDays}</div>
          <div className="text-gray-600">Total Days</div>
        </div>

        <div className="grace-card text-center">
          <div className="w-12 h-12 mx-auto bg-gradient-to-r from-saint-blue to-divine-purple rounded-full flex items-center justify-center mb-3">
            <TrendingUp size={24} className="text-white" />
          </div>
          <div className="text-2xl font-bold text-gray-900">{completionPercentage.toFixed(1)}%</div>
          <div className="text-gray-600">Complete</div>
        </div>
      </div>

      {/* Progress Bar */}
      <div className="grace-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Overall Progress</h3>
        <div className="space-y-3">
          <div className="flex justify-between text-sm text-gray-600">
            <span>Progress</span>
            <span>{completionPercentage.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-4">
            <div
              className="bg-gradient-to-r from-saint-blue to-divine-purple h-4 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(completionPercentage, 100)}%` }}
            ></div>
          </div>
          <div className="text-sm text-gray-600 text-center">
            {daysCompleted} of {totalDays} days completed
          </div>
        </div>
      </div>

      {/* Milestones */}
      <div className="grace-card">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Milestones</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {[25, 50, 75, 100].map((milestone) => {
            const achieved = completionPercentage >= milestone;
            return (
              <div
                key={milestone}
                className={`p-4 rounded-lg text-center ${
                  achieved
                    ? 'bg-green-50 border-2 border-green-200'
                    : 'bg-gray-50 border-2 border-gray-200'
                }`}
              >
                <div className={`text-2xl font-bold mb-1 ${
                  achieved ? 'text-green-700' : 'text-gray-400'
                }`}>
                  {milestone}%
                </div>
                <div className={`text-sm ${
                  achieved ? 'text-green-600' : 'text-gray-500'
                }`}>
                  {achieved ? '✓ Achieved' : 'In Progress'}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Encouragement */}
      <div className="bg-gradient-to-r from-blue-50 to-purple-50 p-6 rounded-lg border border-gray-200">
        <div className="text-center">
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            {completionPercentage < 25 ? 'Just Getting Started' :
             completionPercentage < 50 ? 'Making Great Progress' :
             completionPercentage < 75 ? 'Halfway There!' :
             completionPercentage < 100 ? 'Almost Complete!' :
             'Congratulations!'}
          </h3>
          <p className="text-gray-700">
            {completionPercentage < 25
              ? "Every journey begins with a single step. Keep reading and reflecting!"
              : completionPercentage < 50
              ? "You're building a wonderful habit. Stay consistent and watch your spiritual growth!"
              : completionPercentage < 75
              ? "Halfway through the year! Your dedication is inspiring."
              : completionPercentage < 100
              ? "The finish line is in sight. You've accomplished something remarkable!"
              : "You've completed the Bible in a Year! What an incredible achievement!"}
          </p>
        </div>
      </div>
    </div>
  );
};