import axios, { AxiosResponse } from 'axios';
import {
  DailyReading,
  DiaryEntry,
  CommentaryRequest,
  CommentaryResponse,
  QuestionRequest,
  QuestionResponse,
  ReadingProgress,
  AIHelper,
  ApiResponse
} from '../types';

// Configure axios instance
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for offline handling
api.interceptors.request.use(
  (config) => {
    // Check if we're online
    if (!navigator.onLine) {
      // Could queue requests for later
      console.warn('Request made while offline:', config.url);
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (!navigator.onLine) {
      console.error('Network request failed - device appears offline');
      // Could show offline message
    }
    return Promise.reject(error);
  }
);

export class BibleApiService {
  // Reading endpoints
  static async getDailyReading(date: string): Promise<DailyReading> {
    const response: AxiosResponse<DailyReading> = await api.get(`/readings/${date}`);
    return response.data;
  }

  // Diary endpoints
  static async getDiaryEntry(date: string): Promise<DiaryEntry | null> {
    try {
      const response: AxiosResponse<DiaryEntry> = await api.get(`/diary/${date}`);
      return response.data.exists ? response.data : null;
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 404) {
        return null;
      }
      throw error;
    }
  }

  static async saveDiaryEntry(entry: Omit<DiaryEntry, 'created_at' | 'updated_at'>): Promise<ApiResponse<void>> {
    const response: AxiosResponse<ApiResponse<void>> = await api.post('/diary', entry);
    return response.data;
  }

  // AI Helper endpoints
  static async getCommentary(request: CommentaryRequest): Promise<CommentaryResponse> {
    const response: AxiosResponse<CommentaryResponse> = await api.post('/commentary', request);
    return response.data;
  }

  static async askQuestion(request: QuestionRequest): Promise<QuestionResponse> {
    const response: AxiosResponse<QuestionResponse> = await api.post('/ask', request);
    return response.data;
  }

  static async getAvailableHelpers(): Promise<{ helpers: AIHelper[] }> {
    const response: AxiosResponse<{ helpers: AIHelper[] }> = await api.get('/helpers');
    return response.data;
  }

  // Progress endpoints
  static async getReadingProgress(): Promise<ReadingProgress> {
    const response: AxiosResponse<ReadingProgress> = await api.get('/progress');
    return response.data;
  }

  // Utility endpoints
  static async getAppInfo(): Promise<any> {
    const response: AxiosResponse<any> = await api.get('/');
    return response.data;
  }
}

// Offline queue management
export class OfflineQueue {
  private static readonly STORAGE_KEY = 'bible_app_offline_queue';

  static async addToQueue(item: {
    type: 'diary' | 'question' | 'commentary';
    data: any;
    id: string;
  }): Promise<void> {
    const queue = this.getQueue();
    queue.push({
      ...item,
      timestamp: new Date().toISOString(),
      retryCount: 0,
    });
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(queue));
  }

  static getQueue(): any[] {
    try {
      const stored = localStorage.getItem(this.STORAGE_KEY);
      return stored ? JSON.parse(stored) : [];
    } catch {
      return [];
    }
  }

  static removeFromQueue(id: string): void {
    const queue = this.getQueue().filter(item => item.id !== id);
    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(queue));
  }

  static clearQueue(): void {
    localStorage.removeItem(this.STORAGE_KEY);
  }

  static async processQueue(): Promise<void> {
    if (!navigator.onLine) return;

    const queue = this.getQueue();
    const remainingItems = [];

    for (const item of queue) {
      try {
        switch (item.type) {
          case 'diary':
            await BibleApiService.saveDiaryEntry(item.data);
            break;
          case 'question':
            await BibleApiService.askQuestion(item.data);
            break;
          case 'commentary':
            await BibleApiService.getCommentary(item.data);
            break;
        }
        // Success - don't add to remaining items
      } catch (error) {
        item.retryCount++;
        if (item.retryCount < 3) {
          remainingItems.push(item);
        } else {
          console.warn('Failed to process queued item after 3 retries:', item);
        }
      }
    }

    localStorage.setItem(this.STORAGE_KEY, JSON.stringify(remainingItems));
  }
}

// Network status monitoring
export class NetworkMonitor {
  private static listeners: ((online: boolean) => void)[] = [];

  static init(): void {
    window.addEventListener('online', () => this.notifyListeners(true));
    window.addEventListener('offline', () => this.notifyListeners(false));

    // Process offline queue when coming back online
    window.addEventListener('online', () => {
      OfflineQueue.processQueue();
    });
  }

  static addListener(callback: (online: boolean) => void): void {
    this.listeners.push(callback);
  }

  static removeListener(callback: (online: boolean) => void): void {
    this.listeners = this.listeners.filter(listener => listener !== callback);
  }

  private static notifyListeners(online: boolean): void {
    this.listeners.forEach(listener => listener(online));
  }

  static isOnline(): boolean {
    return navigator.onLine;
  }
}

// Initialize network monitoring
NetworkMonitor.init();