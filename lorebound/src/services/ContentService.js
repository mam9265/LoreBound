/**
 * ContentService - Handles all content-related API calls (dungeons, questions)
 */
import { API_BASE_URL, API_TIMEOUT } from '../config/config';
import AuthUtils from './authUtils';

class ContentService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = API_TIMEOUT;
  }

  /**
   * Make a fetch request with timeout and authentication
   */
  async fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeoutId);
      return response;
    } catch (error) {
      clearTimeout(timeoutId);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  /**
   * Get all available dungeons
   * @returns {Promise<Array>} Array of dungeon objects
   */
  async getDungeons() {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/content/dungeons`,
          {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to fetch dungeons');
        }

        return data;
      } catch (error) {
        console.error('Get dungeons error:', error);
        throw error;
      }
    });
  }

  /**
   * Get a specific dungeon by ID
   * @param {string} dungeonId - UUID of the dungeon
   * @returns {Promise<Object>} Dungeon object with tiers
   */
  async getDungeonById(dungeonId) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/content/dungeons/${dungeonId}`,
          {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to fetch dungeon');
        }

        return data;
      } catch (error) {
        console.error('Get dungeon by ID error:', error);
        throw error;
      }
    });
  }

  /**
   * Get questions for a dungeon
   * @param {string} dungeonId - UUID of the dungeon
   * @param {number} floor - Floor number
   * @param {number} count - Number of questions (default: 10)
   * @returns {Promise<Array>} Array of question objects
   */
  async getQuestions(dungeonId, floor = 1, count = 10) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/content/questions?dungeon_id=${dungeonId}&floor=${floor}&count=${count}`,
          {
            method: 'GET',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to fetch questions');
        }

        return data;
      } catch (error) {
        console.error('Get questions error:', error);
        throw error;
      }
    });
  }

  /**
   * Get category display name
   * @param {string} category - Category enum value
   * @returns {string} Display name
   */
  getCategoryDisplayName(category) {
    const displayNames = {
      'history': 'History',
      'sports': 'Sports',
      'music': 'Music',
      'pop_culture': 'Pop Culture',
      'all_around': 'All Around',
      'books': 'Books',
    };
    return displayNames[category] || category;
  }

  /**
   * Get category icon/emoji
   * @param {string} category - Category enum value
   * @returns {string} Emoji or icon
   */
  getCategoryIcon(category) {
    const icons = {
      'history': '🏛️',
      'sports': '⚽',
      'music': '🎵',
      'pop_culture': '📺',
      'all_around': '🌟',
      'books': '📚',
    };
    return icons[category] || '❓';
  }
}

// Export singleton instance
export default new ContentService();

