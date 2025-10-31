/**
 * LeaderboardService - Handles all leaderboard related API calls
 */
import { API_BASE_URL, API_TIMEOUT } from '../config/config';
import AuthUtils from './authUtils';

class LeaderboardService {
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
   * Get leaderboard rankings for specified scope
   * @param {string} scope - Time scope: 'today', 'weekly', 'alltime'
   * @param {number} limit - Number of entries to return (1-100)
   * @param {number} offset - Offset for pagination
   * @returns {Promise<Object>} Leaderboard data with entries
   */
  async getLeaderboard(scope = 'alltime', limit = 100, offset = 0) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const url = `${this.baseURL}/v1/leaderboards/?scope=${scope}&limit=${limit}&offset=${offset}`;
        const response = await this.fetchWithTimeout(url, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Failed to fetch leaderboard: ${response.status}`);
        }

        return await response.json();
      } catch (error) {
        console.error('Error fetching leaderboard:', error);
        throw error;
      }
    });
  }

  /**
   * Get current user's rank and neighboring players
   * @param {string} scope - Time scope: 'today', 'weekly', 'alltime'
   * @param {number} neighbors - Number of neighbors to show (0-10)
   * @returns {Promise<Object>} User rank data with neighbors
   */
  async getMyRank(scope = 'alltime', neighbors = 3) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const url = `${this.baseURL}/v1/leaderboards/me?scope=${scope}&neighbors=${neighbors}`;
        const response = await this.fetchWithTimeout(url, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Failed to fetch user rank: ${response.status}`);
        }

        return await response.json();
      } catch (error) {
        console.error('Error fetching user rank:', error);
        throw error;
      }
    });
  }

  /**
   * Get leaderboard statistics for specified scope
   * @param {string} scope - Time scope: 'today', 'weekly', 'alltime'
   * @returns {Promise<Object>} Leaderboard statistics
   */
  async getLeaderboardStats(scope = 'alltime') {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const url = `${this.baseURL}/v1/leaderboards/stats?scope=${scope}`;
        const response = await this.fetchWithTimeout(url, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          const errorData = await response.json().catch(() => ({}));
          throw new Error(errorData.detail || `Failed to fetch leaderboard stats: ${response.status}`);
        }

        return await response.json();
      } catch (error) {
        console.error('Error fetching leaderboard stats:', error);
        throw error;
      }
    });
  }

  /**
   * Format scope display name
   * @param {string} scope - Time scope
   * @returns {string} Display name
   */
  getScopeDisplayName(scope) {
    const scopeNames = {
      'today': 'Today',
      'weekly': 'This Week',
      'alltime': 'All-Time',
    };
    return scopeNames[scope] || 'All-Time';
  }

  /**
   * Get cache duration for client-side caching (in milliseconds)
   * @param {string} scope - Time scope
   * @returns {number} Cache duration in ms
   */
  getCacheDuration(scope) {
    const cacheDurations = {
      'today': 30000,    // 30 seconds for today
      'weekly': 60000,   // 1 minute for weekly
      'alltime': 300000, // 5 minutes for all-time
    };
    return cacheDurations[scope] || 300000;
  }
}

// Export singleton instance
export default new LeaderboardService();

