import React, { useState, useEffect } from 'react';
import { Users, MessageCircle, Sparkles } from 'lucide-react';
import { BibleApiService } from '../services/api';
import { AIHelper, QuestionResponse } from '../types';

export const AIHelpers: React.FC = () => {
  const [helpers, setHelpers] = useState<AIHelper[]>([]);
  const [selectedHelper, setSelectedHelper] = useState<string>('augustine');
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<QuestionResponse | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadHelpers();
  }, []);

  const loadHelpers = async () => {
    try {
      const response = await BibleApiService.getAvailableHelpers();
      setHelpers(response.helpers);
    } catch (error) {
      console.error('Failed to load AI helpers:', error);
    }
  };

  const askQuestion = async () => {
    if (!question.trim()) return;

    setLoading(true);
    try {
      const response = await BibleApiService.askQuestion({
        question: question.trim(),
        helper: selectedHelper
      });
      setAnswer(response);
    } catch (error) {
      console.error('Failed to get answer:', error);
    } finally {
      setLoading(false);
    }
  };

  const selectedHelperInfo = helpers.find(h => h.id === selectedHelper);

  return (
    <div className="space-y-6">
      <div className="text-center">
        <div className="w-16 h-16 mx-auto bg-gradient-to-r from-saint-blue to-divine-purple rounded-full flex items-center justify-center mb-4">
          <Users size={32} className="text-white" />
        </div>
        <h2 className="text-2xl font-bold text-gray-900">AI Spiritual Companions</h2>
        <p className="text-gray-600 mt-2 max-w-2xl mx-auto">
          Engage in spiritual conversation with Saints Augustine and Aquinas.
          Ask questions about Scripture, theology, and the spiritual life.
        </p>
      </div>

      {/* Helper Selection */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {helpers.map((helper) => (
          <div
            key={helper.id}
            onClick={() => setSelectedHelper(helper.id)}
            className={`grace-card cursor-pointer transition-all ${
              selectedHelper === helper.id
                ? 'ring-2 ring-saint-blue shadow-lg'
                : 'hover:shadow-md'
            }`}
          >
            <div className="flex items-center space-x-3 mb-3">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center ${
                helper.id === 'augustine' ? 'bg-saint-blue' :
                helper.id === 'aquinas' ? 'bg-divine-purple' :
                'bg-gradient-to-r from-saint-blue to-divine-purple'
              }`}>
                <Users size={20} className="text-white" />
              </div>
              <h3 className="font-semibold text-gray-900">{helper.name}</h3>
            </div>
            <p className="text-sm text-gray-600 mb-3">{helper.description}</p>
            <div className="flex flex-wrap gap-1">
              {helper.specialties.map((specialty, index) => (
                <span
                  key={index}
                  className="px-2 py-1 bg-gray-100 text-xs rounded-full text-gray-700"
                >
                  {specialty}
                </span>
              ))}
            </div>
          </div>
        ))}
      </div>

      {/* Question Interface */}
      <div className="grace-card">
        <div className="flex items-center space-x-2 mb-4">
          <MessageCircle className="text-saint-blue" size={20} />
          <h3 className="text-lg font-semibold text-gray-900">
            Ask {selectedHelperInfo?.name}
          </h3>
        </div>

        <div className="space-y-4">
          <textarea
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder={`Ask ${selectedHelperInfo?.name} a question about Scripture, theology, or spiritual guidance...`}
            className="w-full h-24 p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-saint-blue focus:border-transparent resize-vertical"
            rows={4}
          />

          <div className="flex justify-between items-center">
            <div className="text-sm text-gray-600">
              {question.length} characters
            </div>
            <button
              onClick={askQuestion}
              disabled={!question.trim() || loading}
              className="flex items-center space-x-2 px-6 py-2 bg-gradient-to-r from-saint-blue to-divine-purple text-white rounded-lg hover:from-blue-700 hover:to-purple-700 transition-colors disabled:opacity-50"
            >
              {loading ? (
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
              ) : (
                <Sparkles size={18} />
              )}
              <span>{loading ? 'Thinking...' : 'Ask Question'}</span>
            </button>
          </div>
        </div>
      </div>

      {/* Answer Display */}
      {answer && (
        <div className="grace-card">
          <div className={`p-4 rounded-lg mb-4 ${
            answer.helper === 'augustine' ? 'saint-augustine' :
            answer.helper === 'aquinas' ? 'saint-aquinas' :
            'bg-gradient-to-r from-saint-blue to-divine-purple text-white'
          }`}>
            <div className="flex items-center space-x-2">
              <Users size={20} />
              <span className="font-semibold">
                {answer.helper === 'combined' ? 'Combined Wisdom' : `Saint ${answer.helper}`}
              </span>
            </div>
          </div>

          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Your Question</h4>
              <p className="text-gray-700 italic">"{answer.question}"</p>
            </div>

            <div>
              <h4 className="font-medium text-gray-900 mb-2">Response</h4>
              <div className="prose prose-gray max-w-none">
                <div className="text-gray-800 leading-relaxed whitespace-pre-wrap font-serif">
                  {answer.answer}
                </div>
              </div>
            </div>

            <div className="text-xs text-gray-500 pt-4 border-t border-gray-200">
              Generated: {new Date(answer.timestamp).toLocaleString()}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};