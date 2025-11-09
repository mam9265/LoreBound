/**
 * RunService - Handles all dungeon run related API calls
 */
import { API_BASE_URL, API_TIMEOUT } from '../config/config';
import AuthUtils from './authUtils';

class RunService {
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
   * Start a new dungeon run
   * @param {string} dungeonId - UUID of the dungeon
   * @param {number} floor - Starting floor (default: 1)
   * @param {object} clientMetadata - Optional client metadata
   * @returns {Promise<Object>} Run data with session token and seed
   */
  async startRun(dungeonId, floor = 1, clientMetadata = {}) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(`${this.baseURL}/v1/runs/start`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            dungeon_id: dungeonId,
            floor,
            client_metadata: {
              ...clientMetadata,
              timestamp: Date.now(),
            },
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to start run');
        }

        return data;
      } catch (error) {
        console.error('Start run error:', error);
        throw error;
      }
    });
  }

  /**
   * Submit a completed run
   * @param {string} runId - UUID of the run
   * @param {Array} turnData - Array of turn data objects
   * @param {Array} scores - Array of score data objects
   * @param {string} clientSignature - HMAC signature for anti-cheat
   * @param {boolean} isVictory - Whether the player won/cleared the dungeon
   * @param {boolean} isDailyChallenge - Whether this was a daily challenge
   * @returns {Promise<Object>} Completed run data
   */
  async submitRun(runId, turnData, scores, clientSignature, isVictory = true, isDailyChallenge = false) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/runs/${runId}/submit`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              turn_data: turnData,
              scores: scores,
              client_signature: clientSignature,
              is_victory: isVictory,
              is_daily_challenge: isDailyChallenge,
            }),
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to submit run');
        }

        return data;
      } catch (error) {
        console.error('Submit run error:', error);
        throw error;
      }
    });
  }

  /**
   * Get user's run history
   * @param {number} limit - Number of runs to fetch (default: 20)
   * @param {number} offset - Offset for pagination (default: 0)
   * @returns {Promise<Array>} Array of run objects
   */
  async getUserRuns(limit = 20, offset = 0) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/runs/?limit=${limit}&offset=${offset}`,
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
          throw new Error(data.detail || 'Failed to fetch runs');
        }

        return data;
      } catch (error) {
        console.error('Get user runs error:', error);
        throw error;
      }
    });
  }

  /**
   * Get specific run details
   * @param {string} runId - UUID of the run
   * @returns {Promise<Object>} Run details
   */
  async getRunById(runId) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/runs/${runId}`,
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
          throw new Error(data.detail || 'Failed to fetch run');
        }

        return data;
      } catch (error) {
        console.error('Get run by ID error:', error);
        throw error;
      }
    });
  }

  /**
   * Abandon a run in progress
   * @param {string} runId - UUID of the run
   * @returns {Promise<Object>} Abandoned run data
   */
  async abandonRun(runId) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/runs/${runId}/abandon`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to abandon run');
        }

        return data;
      } catch (error) {
        console.error('Abandon run error:', error);
        throw error;
      }
    });
  }

  /**
   * Get user's game statistics
   * @returns {Promise<Object>} User stats including total runs, scores, accuracy
   */
  async getUserStats() {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/runs/stats/me`,
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
          throw new Error(data.detail || 'Failed to fetch stats');
        }

        return data;
      } catch (error) {
        console.error('Get user stats error:', error);
        throw error;
      }
    });
  }

  /**
   * Get questions for a run (deterministic based on seed)
   * @param {string} dungeonId - UUID of the dungeon
   * @param {number} seed - Run seed for deterministic questions (unused, kept for compatibility)
   * @param {number} count - Number of questions (default: 10)
   * @param {number} floor - Floor number (default: 1)
   * @returns {Promise<Array>} Array of question objects
   */
  async getQuestionsForRun(dungeonId, seed, count = 10, floor = 1) {
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

        // API returns { questions: [...], seed, dungeon_id, floor }
        // We need to return just the questions array
        return data.questions || [];
      } catch (error) {
        console.error('Get questions error:', error);
        throw error;
      }
    });
  }

  /**
   * Validate a single answer in real-time
   * @param {string} runId - UUID of the run
   * @param {string} questionId - UUID of the question
   * @param {number} answerIndex - Index of selected answer
   * @returns {Promise<Object>} Validation result with is_correct
   */
  async validateAnswer(runId, questionId, answerIndex) {
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(
          `${this.baseURL}/v1/runs/${runId}/validate-answer?question_id=${questionId}&answer_index=${answerIndex}`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to validate answer');
        }

        return data;
      } catch (error) {
        console.error('Validate answer error:', error);
        throw error;
      }
    });
  }

  /**
   * Calculate HMAC signature for anti-cheat
   * @param {object} turnData - Turn data to sign
   * @param {string} sessionToken - Session token from run start
   * @returns {string} HMAC signature
   */
  async calculateTurnSignature(turnData, sessionToken) {
    // Simple signature for now - in production use crypto library
    const dataString = JSON.stringify(turnData) + sessionToken;
    // For now return a simple hash, TODO: implement proper HMAC
    return btoa(dataString).substring(0, 32);
  }

  /**
   * Calculate aggregate signature for run submission
   * @param {Array} turnData - Array of all turn data
   * @param {string} sessionToken - Session token
   * @returns {string} Aggregate signature
   */
  async calculateAggregateSignature(turnData, sessionToken) {
    // Aggregate all turn signatures
    const aggregateData = turnData.map(t => t.h).join('') + sessionToken;
    return btoa(aggregateData).substring(0, 64);
  }
}

// Export singleton instance
export default new RunService();

