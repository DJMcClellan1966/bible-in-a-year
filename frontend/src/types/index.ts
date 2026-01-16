// Type definitions for Bible in a Year App

export interface BiblePassage {
  reference: string;
  text: { [verse: string]: string };
  citation: string;
  note?: string;
}

export interface DailyReading {
  date: string;
  passages: string[];
  theme?: string;
  text?: { [passage: string]: BiblePassage };
  total_verses?: number;
}

export interface DiaryEntry {
  date: string;
  reading_passage: string;
  personal_notes?: string;
  margin_notes?: { [key: string]: string };
  ai_insights?: string;
  created_at?: string;
  updated_at?: string;
}

export interface AIHelper {
  id: string;
  name: string;
  description: string;
  specialties: string[];
}

export interface CommentaryRequest {
  passage: string;
  helper: string;
  personalized?: boolean;
}

export interface CommentaryResponse {
  passage: string;
  helper: string;
  commentary: string;
  timestamp: string;
}

export interface QuestionRequest {
  question: string;
  context?: string;
  helper: string;
}

export interface QuestionResponse {
  question: string;
  helper: string;
  answer: string;
  timestamp: string;
}

export interface ReadingProgress {
  total_readings: number;
  completed_readings: number;
  completion_percentage: number;
}

export interface UserPreferences {
  theme: 'light' | 'dark' | 'auto';
  fontSize: 'small' | 'medium' | 'large';
  defaultHelper: string;
  notifications: boolean;
  offlineMode: boolean;
}

export interface MarginNote {
  id: string;
  verse?: string;
  note: string;
  timestamp: string;
  category?: 'reflection' | 'question' | 'insight' | 'prayer';
}

// API Response types
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  message?: string;
}

// Reading Plan types
export interface ReadingPlan {
  name: string;
  description: string;
  total_days: number;
  start_date: string;
  readings: { [date: string]: DailyReading };
}

// Search types
export interface SearchResult {
  reference: string;
  text: string;
  relevance_score: number;
}

// Offline support types
export interface OfflineQueueItem {
  id: string;
  type: 'diary' | 'question' | 'commentary';
  data: any;
  timestamp: string;
  retryCount: number;
}