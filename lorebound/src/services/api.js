/**
 * API service for making HTTP requests to the backend
 */
import { API_BASE_URL, API_TIMEOUT } from '../config/config';

class ApiService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = API_TIMEOUT;
  }

  /**
   * Make a fetch request with timeout
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
   * Login user with email and password
   * @param {string} email - User email
   * @param {string} password - User password
   * @returns {Promise<Object>} Response with tokens and user data
   */
  async login(email, password) {
    try {
      const response = await this.fetchWithTimeout(`${this.baseURL}/v1/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.toLowerCase().trim(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle validation errors (422) with detailed messages
        if (response.status === 422 && data.detail) {
          throw new Error(data.detail);
        }
        // Handle other errors
        const errorMessage = data.detail || data.message || 'Login failed';
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      console.error('Login error:', error);
      // If error already has a message, re-throw it; otherwise wrap it
      if (error.message) {
        throw error;
      }
      throw new Error(error.toString() || 'Login failed');
    }
  }

  /**
   * Register new user
   * @param {string} email - User email
   * @param {string} handle - User handle/username
   * @param {string} password - User password
   * @returns {Promise<Object>} Response with tokens and user data
   */
  async register(email, handle, password) {
    try {
      const response = await this.fetchWithTimeout(`${this.baseURL}/v1/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email.toLowerCase().trim(),
          handle: handle.trim(),
          password,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        // Handle validation errors (422) with detailed messages
        if (response.status === 422 && data.detail) {
          throw new Error(data.detail);
        }
        // Handle other errors
        const errorMessage = data.detail || data.message || 'Registration failed';
        throw new Error(errorMessage);
      }

      return data;
    } catch (error) {
      console.error('Registration error:', error);
      // If error already has a message, re-throw it; otherwise wrap it
      if (error.message) {
        throw error;
      }
      throw new Error(error.toString() || 'Registration failed');
    }
  }

  /**
   * Refresh authentication token
   * @param {string} refreshToken - Refresh token
   * @returns {Promise<Object>} New tokens
   */
  async refreshToken(refreshToken) {
    try {
      const response = await this.fetchWithTimeout(`${this.baseURL}/v1/auth/refresh`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          refresh_token: refreshToken,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Token refresh failed');
      }

      return data;
    } catch (error) {
      console.error('Token refresh error:', error);
      throw error;
    }
  }

  /**
   * Get current user profile
   * @param {string} accessToken - Access token
   * @returns {Promise<Object>} User profile data
   */
  async getCurrentUser(accessToken) {
    try {
      const response = await this.fetchWithTimeout(`${this.baseURL}/v1/auth/me`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to get user profile');
      }

      return data;
    } catch (error) {
      console.error('Get user profile error:', error);
      throw error;
    }
  }

  /**
   * Logout user
   * @param {string} accessToken - Access token
   * @returns {Promise<Object>} Logout response
   */
  async logout(accessToken) {
    try {
      const response = await this.fetchWithTimeout(`${this.baseURL}/v1/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${accessToken}`,
          'Content-Type': 'application/json',
        },
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Logout failed');
      }

      return data;
    } catch (error) {
      console.error('Logout error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export default new ApiService();

