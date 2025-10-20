/**
 * Authentication utility functions
 * Helpers for managing authentication state, tokens, and user data
 */
import AsyncStorage from '@react-native-async-storage/async-storage';
import ApiService from './api';

class AuthUtils {
  /**
   * Store authentication tokens
   * @param {string} accessToken - JWT access token
   * @param {string} refreshToken - JWT refresh token
   */
  async storeTokens(accessToken, refreshToken) {
    try {
      await AsyncStorage.setItem('access_token', accessToken);
      await AsyncStorage.setItem('refresh_token', refreshToken);
    } catch (error) {
      console.error('Error storing tokens:', error);
      throw error;
    }
  }

  /**
   * Get stored access token
   * @returns {Promise<string|null>} Access token or null
   */
  async getAccessToken() {
    try {
      return await AsyncStorage.getItem('access_token');
    } catch (error) {
      console.error('Error getting access token:', error);
      return null;
    }
  }

  /**
   * Get stored refresh token
   * @returns {Promise<string|null>} Refresh token or null
   */
  async getRefreshToken() {
    try {
      return await AsyncStorage.getItem('refresh_token');
    } catch (error) {
      console.error('Error getting refresh token:', error);
      return null;
    }
  }

  /**
   * Store user data
   * @param {Object} userData - User data object
   */
  async storeUserData(userData) {
    try {
      await AsyncStorage.setItem('user_data', JSON.stringify(userData));
    } catch (error) {
      console.error('Error storing user data:', error);
      throw error;
    }
  }

  /**
   * Get stored user data
   * @returns {Promise<Object|null>} User data or null
   */
  async getUserData() {
    try {
      const data = await AsyncStorage.getItem('user_data');
      return data ? JSON.parse(data) : null;
    } catch (error) {
      console.error('Error getting user data:', error);
      return null;
    }
  }

  /**
   * Clear all authentication data
   */
  async clearAuthData() {
    try {
      await AsyncStorage.multiRemove(['access_token', 'refresh_token', 'user_data']);
      console.log('Auth data cleared');
    } catch (error) {
      console.error('Error clearing auth data:', error);
      throw error;
    }
  }

  /**
   * Check if user is authenticated
   * @returns {Promise<boolean>} True if user has valid tokens
   */
  async isAuthenticated() {
    try {
      const accessToken = await this.getAccessToken();
      return !!accessToken;
    } catch (error) {
      console.error('Error checking authentication:', error);
      return false;
    }
  }

  /**
   * Logout user - clear tokens and call logout endpoint
   */
  async logout() {
    try {
      const accessToken = await this.getAccessToken();
      
      // Call logout endpoint if we have a token
      if (accessToken) {
        try {
          await ApiService.logout(accessToken);
        } catch (error) {
          // Continue with local logout even if API call fails
          console.error('Logout API call failed:', error);
        }
      }
      
      // Clear local storage
      await this.clearAuthData();
      console.log('User logged out');
    } catch (error) {
      console.error('Error during logout:', error);
      throw error;
    }
  }

  /**
   * Refresh access token using refresh token
   * @returns {Promise<string|null>} New access token or null
   */
  async refreshAccessToken() {
    try {
      const refreshToken = await this.getRefreshToken();
      
      if (!refreshToken) {
        console.log('No refresh token available');
        return null;
      }

      const response = await ApiService.refreshToken(refreshToken);
      
      // Store new tokens
      await this.storeTokens(response.access_token, response.refresh_token);
      
      return response.access_token;
    } catch (error) {
      console.error('Error refreshing token:', error);
      // If refresh fails, clear all auth data
      await this.clearAuthData();
      return null;
    }
  }

  /**
   * Get current user profile from backend
   * @returns {Promise<Object|null>} User profile or null
   */
  async getCurrentUserProfile() {
    try {
      let accessToken = await this.getAccessToken();
      
      if (!accessToken) {
        console.log('No access token available');
        return null;
      }

      try {
        const profile = await ApiService.getCurrentUser(accessToken);
        await this.storeUserData(profile);
        return profile;
      } catch (error) {
        // If request fails with 401, try to refresh token
        if (error.message.includes('401')) {
          console.log('Token expired, attempting refresh...');
          accessToken = await this.refreshAccessToken();
          
          if (accessToken) {
            const profile = await ApiService.getCurrentUser(accessToken);
            await this.storeUserData(profile);
            return profile;
          }
        }
        throw error;
      }
    } catch (error) {
      console.error('Error getting user profile:', error);
      return null;
    }
  }

  /**
   * Make authenticated API request with automatic token refresh
   * @param {Function} apiCall - Function that makes the API call
   * @returns {Promise<any>} API response
   */
  async authenticatedRequest(apiCall) {
    try {
      let accessToken = await this.getAccessToken();
      
      if (!accessToken) {
        throw new Error('No access token available');
      }

      try {
        return await apiCall(accessToken);
      } catch (error) {
        // If request fails with 401, try to refresh token
        if (error.message.includes('401') || error.message.includes('Unauthorized')) {
          console.log('Token expired, attempting refresh...');
          accessToken = await this.refreshAccessToken();
          
          if (accessToken) {
            return await apiCall(accessToken);
          }
          
          throw new Error('Authentication failed');
        }
        throw error;
      }
    } catch (error) {
      console.error('Authenticated request error:', error);
      throw error;
    }
  }
}

// Export singleton instance
export default new AuthUtils();

