import React from 'react';
import { Heart, Github, BookOpen } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-gray-900 text-white mt-16">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {/* App Info */}
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-8 h-8 bg-gradient-to-r from-saint-blue to-divine-purple rounded-lg flex items-center justify-center">
                <BookOpen size={16} className="text-white" />
              </div>
              <span className="font-bold text-lg">Bible in a Year</span>
            </div>
            <p className="text-gray-400 text-sm leading-relaxed">
              Embark on a transformative journey through Scripture with AI-powered insights
              from Saints Augustine and Aquinas. Experience the Bible like never before.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Quick Links</h3>
            <ul className="space-y-2 text-gray-400">
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Daily Reading Plan
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  AI Spiritual Companions
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Reading Progress
                </a>
              </li>
              <li>
                <a href="#" className="hover:text-white transition-colors">
                  Personal Diary
                </a>
              </li>
            </ul>
          </div>

          {/* Credits and Links */}
          <div>
            <h3 className="font-semibold text-lg mb-4">Resources & Credits</h3>
            <ul className="space-y-2 text-gray-400 text-sm">
              <li>
                <a href="https://ccel.org" target="_blank" rel="noopener noreferrer"
                   className="hover:text-white transition-colors">
                  Christian Classics Ethereal Library
                </a>
              </li>
              <li>
                <a href="https://www.gutenberg.org" target="_blank" rel="noopener noreferrer"
                   className="hover:text-white transition-colors">
                  Project Gutenberg
                </a>
              </li>
              <li>
                <a href="https://archive.org" target="_blank" rel="noopener noreferrer"
                   className="hover:text-white transition-colors">
                  Internet Archive
                </a>
              </li>
              <li>
                <a href="https://ollama.ai" target="_blank" rel="noopener noreferrer"
                   className="hover:text-white transition-colors">
                  Ollama AI
                </a>
              </li>
            </ul>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 mt-8 pt-6">
          <div className="flex flex-col md:flex-row items-center justify-between">
            <div className="flex items-center space-x-2 text-gray-400 text-sm mb-4 md:mb-0">
              <span>Made with</span>
              <Heart size={14} className="text-red-500 fill-current" />
              <span>for spiritual growth and learning</span>
            </div>

            <div className="flex items-center space-x-4 text-sm text-gray-400">
              <span>&copy; 2024 Bible in a Year App</span>
              <span>•</span>
              <a href="#" className="hover:text-white transition-colors flex items-center space-x-1">
                <Github size={14} />
                <span>Source</span>
              </a>
              <span>•</span>
              <span className="text-xs">v1.0.0</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};