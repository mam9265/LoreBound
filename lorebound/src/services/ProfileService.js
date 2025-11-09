/**
 * Profile Service
 * Handles API calls for user profile and character customization
 */

import { API_BASE_URL } from '../config/config';
import AuthUtils from './authUtils';
import CacheService from './CacheService';

class ProfileService {
  constructor() {
    this.baseURL = API_BASE_URL;
    this.timeout = 10000; // 10 seconds
  }

  /**
   * Fetch with timeout
   */
  async fetchWithTimeout(url, options = {}) {
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...options,
        signal: controller.signal,
      });
      clearTimeout(timeout);
      return response;
    } catch (error) {
      clearTimeout(timeout);
      if (error.name === 'AbortError') {
        throw new Error('Request timeout');
      }
      throw error;
    }
  }

  /**
   * Get user profile (with caching)
   * @param {boolean} forceRefresh - Force refresh from backend, skip cache
   * @returns {Promise<Object>} User profile data
   */
  async getProfile(forceRefresh = false) {
    // Try cache first unless force refresh
    if (!forceRefresh) {
      const cached = await CacheService.getProfile();
      if (cached) {
        console.log('[ProfileService] Using cached profile');
        return cached;
      }
    }

    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        console.log('[ProfileService] Fetching profile from backend');
        
        const response = await this.fetchWithTimeout(`${this.baseURL}/v1/profile/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to get profile');
        }

        // Cache the profile data
        await CacheService.setProfile(data);
        if (data.avatar_layers && data.avatar_layers.colorIndex !== undefined) {
          await CacheService.setColorIndex(data.avatar_layers.colorIndex);
        }
        
        console.log('[ProfileService] Profile fetched and cached');
        return data;
      } catch (error) {
        console.error('[ProfileService] Get profile error:', error);
        throw error;
      }
    });
  }

  /**
   * Update user profile
   * @param {Object} profileData - Profile data to update
   * @param {string} profileData.handle - New display name (optional)
   * @param {Object} profileData.avatar_layers - Character customization data (optional)
   * @returns {Promise<Object>} Updated profile data
   */
  async updateProfile(profileData) {
    const result = await AuthUtils.authenticatedRequest(async (token) => {
      try {
        const response = await this.fetchWithTimeout(`${this.baseURL}/v1/profile/`, {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(profileData),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to update profile');
        }

        return data;
      } catch (error) {
        console.error('[ProfileService] Update profile error:', error);
        throw error;
      }
    });

    // Update cache with fresh data
    await CacheService.setProfile(result);
    if (result.avatar_layers && result.avatar_layers.colorIndex !== undefined) {
      await CacheService.setColorIndex(result.avatar_layers.colorIndex);
    }
    console.log('[ProfileService] Cache updated after profile update');
    
    return result;
  }

  /**
   * Update character customization only
   * @param {Object} customizationData - Character customization data
   * @returns {Promise<Object>} Updated profile data
   */
  async updateCharacterCustomization(customizationData) {
    return await this.updateProfile({
      avatar_layers: customizationData,
    });
  }

  /**
   * Save character customization from CharacterCustomization component
   * Converts the frontend format to backend format
   * @param {Object} equipment - Equipment data {helmet, armor, weapon, shield}
   * @param {number} colorIndex - Knight color index
   * @returns {Promise<Object>} Updated profile data
   */
  async saveCharacterEquipment(equipment, colorIndex) {
    const customizationData = {
      equipment: equipment,
      colorIndex: colorIndex,
      lastUpdated: new Date().toISOString(),
    };

    return await this.updateCharacterCustomization(customizationData);
  }

  /**
   * Load character customization (with caching)
   * @param {boolean} forceRefresh - Force refresh from backend
   * @returns {Promise<Object>} Character customization data
   */
  async loadCharacterCustomization(forceRefresh = false) {
    try {
      const profile = await this.getProfile(forceRefresh);
      return profile.avatar_layers || null;
    } catch (error) {
      console.error('[ProfileService] Load character customization error:', error);
      return null;
    }
  }

  /**
   * Get cached color index (super fast for knight sprite)
   * @returns {Promise<number|null>} Cached color index or null
   */
  async getCachedColorIndex() {
    return await CacheService.getColorIndex();
  }
}

// Export singleton instance
export default new ProfileService();

