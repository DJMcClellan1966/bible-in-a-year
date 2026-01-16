import React from 'react';
import { CommentaryResponse } from '../types';
import { Users, RefreshCw, Sparkles } from 'lucide-react';

interface AICommentaryProps {
  commentary: CommentaryResponse | null;
  onRequestCommentary: (helper: string) => void;
  loading: boolean;
}

export const AICommentary: React.FC<AICommentaryProps> = ({
  commentary,
  onRequestCommentary,
  loading
}) => {
  const getHelperStyle = (helper: string) => {
    switch (helper) {
      case 'augustine':
        return 'saint-augustine';
      case 'aquinas':
        return 'saint-aquinas';
      default:
        return 'bg-gradient-to-r from-saint-blue to-divine-purple text-white';
    }
  };

  const getHelperIcon = (helper: string) => {
    return <Users size={20} className="text-current" />;
  };

  const getHelperDescription = (helper: string) => {
    switch (helper) {
      case 'augustine':
        return 'Drawing from Confessions and City of God';
      case 'aquinas':
        return 'Drawing from Summa Theologica and systematic theology';
      case 'combined':
        return 'Synthesizing Augustine and Aquinas wisdom';
      default:
        return 'AI-powered spiritual insights';
    }
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center py-12 space-y-4">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-saint-blue"></div>
        <p className="text-gray-600">Consulting the saints...</p>
        <div className="flex items-center space-x-2 text-sm text-gray-500">
          <Sparkles size={16} />
          <span>Generating personalized commentary</span>
        </div>
      </div>
    );
  }

  if (!commentary) {
    return (
      <div className="text-center py-12 space-y-6">
        <div className="w-16 h-16 mx-auto bg-gradient-to-r from-saint-blue to-divine-purple rounded-full flex items-center justify-center">
          <Users size={32} className="text-white" />
        </div>
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">
            AI Spiritual Commentary
          </h3>
          <p className="text-gray-600 max-w-md mx-auto">
            Receive personalized insights and guidance from Saints Augustine and Aquinas
            based on today's reading.
          </p>
        </div>

        <div className="flex flex-col sm:flex-row gap-3 justify-center">
          <button
            onClick={() => onRequestCommentary('augustine')}
            className="flex items-center space-x-2 px-6 py-3 bg-saint-blue text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Users size={18} />
            <span>Ask Saint Augustine</span>
          </button>

          <button
            onClick={() => onRequestCommentary('aquinas')}
            className="flex items-center space-x-2 px-6 py-3 bg-divine-purple text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            <Users size={18} />
            <span>Ask Saint Thomas Aquinas</span>
          </button>

          <button
            onClick={() => onRequestCommentary('combined')}
            className="flex items-center space-x-2 px-6 py-3 bg-gradient-to-r from-saint-blue to-divine-purple text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors"
          >
            <Users size={18} />
            <span>Combined Wisdom</span>
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Commentary Header */}
      <div className={`p-4 rounded-lg ${getHelperStyle(commentary.helper)}`}>
        <div className="flex items-center space-x-3">
          {getHelperIcon(commentary.helper)}
          <div>
            <h3 className="font-semibold text-lg capitalize">
              {commentary.helper === 'combined' ? 'Combined Wisdom' : `Saint ${commentary.helper}`}
            </h3>
            <p className="text-sm opacity-90">
              {getHelperDescription(commentary.helper)}
            </p>
          </div>
        </div>
      </div>

      {/* Commentary Content */}
      <div className="grace-card">
        <div className="flex items-center justify-between mb-4">
          <h4 className="text-lg font-semibold text-gray-900">Spiritual Commentary</h4>
          <button
            onClick={() => onRequestCommentary(commentary.helper)}
            className="flex items-center space-x-2 px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
            disabled={loading}
          >
            <RefreshCw size={14} />
            <span>Refresh</span>
          </button>
        </div>

        <div className="prose prose-gray max-w-none">
          <div className="text-gray-800 leading-relaxed whitespace-pre-wrap font-serif">
            {commentary.commentary}
          </div>
        </div>

        {/* Commentary Meta */}
        <div className="mt-6 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between text-sm text-gray-600">
            <span>
              Commentary on: <span className="font-medium">{commentary.passage}</span>
            </span>
            <span>
              Generated: {new Date(commentary.timestamp).toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Additional Options */}
      <div className="flex flex-wrap gap-3">
        <button
          onClick={() => onRequestCommentary('augustine')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
            commentary.helper === 'augustine'
              ? 'bg-saint-blue text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          disabled={loading}
        >
          <Users size={16} />
          <span>Augustine</span>
        </button>

        <button
          onClick={() => onRequestCommentary('aquinas')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
            commentary.helper === 'aquinas'
              ? 'bg-divine-purple text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          disabled={loading}
        >
          <Users size={16} />
          <span>Aquinas</span>
        </button>

        <button
          onClick={() => onRequestCommentary('combined')}
          className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-colors ${
            commentary.helper === 'combined'
              ? 'bg-gradient-to-r from-saint-blue to-divine-purple text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
          disabled={loading}
        >
          <Users size={16} />
          <span>Combined</span>
        </button>
      </div>
    </div>
  );
};