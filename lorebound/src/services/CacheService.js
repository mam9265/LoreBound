/**
 * Cache Service
 * Handles caching of character data, inventory, and profile to improve loading times
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

class CacheService {
  constructor() {
    // Cache keys
    this.CACHE_KEYS = {
      INVENTORY: 'cache_inventory',
      PROFILE: 'cache_profile',
      COLOR_INDEX: 'cache_colorIndex',
      EQUIPPED_ITEMS: 'cache_equipped_items',
    };

    // Cache TTL (time to live) in milliseconds
    this.TTL = {
      INVENTORY: 5 * 60 * 1000,      // 5 minutes
      PROFILE: 10 * 60 * 1000,       // 10 minutes
      COLOR_INDEX: 30 * 60 * 1000,   // 30 minutes
      EQUIPPED_ITEMS: 5 * 60 * 1000, // 5 minutes
    };
  }

  /**
   * Set cache with timestamp
   * @param {string} key - Cache key
   * @param {any} data - Data to cache
   */
  async set(key, data) {
    try {
      const cacheEntry = {
        data: data,
        timestamp: Date.now(),
      };
      await AsyncStorage.setItem(key, JSON.stringify(cacheEntry));
      console.log(`[CacheService] Cached data for key: ${key}`);
    } catch (error) {
      console.error(`[CacheService] Error setting cache for ${key}:`, error);
    }
  }

  /**
   * Get cached data if not expired
   * @param {string} key - Cache key
   * @param {number} ttl - Time to live in milliseconds
   * @returns {Promise<any|null>} Cached data or null if expired/missing
   */
  async get(key, ttl) {
    try {
      const cached = await AsyncStorage.getItem(key);
      if (!cached) {
        console.log(`[CacheService] No cache found for key: ${key}`);
        return null;
      }

      const cacheEntry = JSON.parse(cached);
      const age = Date.now() - cacheEntry.timestamp;

      if (age > ttl) {
        console.log(`[CacheService] Cache expired for key: ${key} (age: ${age}ms, ttl: ${ttl}ms)`);
        await this.invalidate(key);
        return null;
      }

      console.log(`[CacheService] Cache hit for key: ${key} (age: ${age}ms)`);
      return cacheEntry.data;
    } catch (error) {
      console.error(`[CacheService] Error getting cache for ${key}:`, error);
      return null;
    }
  }

  /**
   * Invalidate (delete) cached data
   * @param {string} key - Cache key
   */
  async invalidate(key) {
    try {
      await AsyncStorage.removeItem(key);
      console.log(`[CacheService] Invalidated cache for key: ${key}`);
    } catch (error) {
      console.error(`[CacheService] Error invalidating cache for ${key}:`, error);
    }
  }

  /**
   * Invalidate all caches
   */
  async invalidateAll() {
    try {
      const keys = Object.values(this.CACHE_KEYS);
      await AsyncStorage.multiRemove(keys);
      console.log('[CacheService] Invalidated all caches');
    } catch (error) {
      console.error('[CacheService] Error invalidating all caches:', error);
    }
  }

  // Convenience methods for specific data types

  /**
   * Cache inventory data
   * @param {Object} inventory - Inventory data
   */
  async setInventory(inventory) {
    await this.set(this.CACHE_KEYS.INVENTORY, inventory);
  }

  /**
   * Get cached inventory
   * @returns {Promise<Object|null>} Cached inventory or null
   */
  async getInventory() {
    return await this.get(this.CACHE_KEYS.INVENTORY, this.TTL.INVENTORY);
  }

  /**
   * Invalidate inventory cache (call when items are equipped/changed)
   */
  async invalidateInventory() {
    await this.invalidate(this.CACHE_KEYS.INVENTORY);
  }

  /**
   * Cache profile data
   * @param {Object} profile - Profile data
   */
  async setProfile(profile) {
    await this.set(this.CACHE_KEYS.PROFILE, profile);
  }

  /**
   * Get cached profile
   * @returns {Promise<Object|null>} Cached profile or null
   */
  async getProfile() {
    return await this.get(this.CACHE_KEYS.PROFILE, this.TTL.PROFILE);
  }

  /**
   * Invalidate profile cache
   */
  async invalidateProfile() {
    await this.invalidate(this.CACHE_KEYS.PROFILE);
  }

  /**
   * Cache color index
   * @param {number} colorIndex - Knight color index
   */
  async setColorIndex(colorIndex) {
    await this.set(this.CACHE_KEYS.COLOR_INDEX, colorIndex);
  }

  /**
   * Get cached color index
   * @returns {Promise<number|null>} Cached color index or null
   */
  async getColorIndex() {
    return await this.get(this.CACHE_KEYS.COLOR_INDEX, this.TTL.COLOR_INDEX);
  }

  /**
   * Cache equipped items
   * @param {Object} equippedItems - Equipped items by slot
   */
  async setEquippedItems(equippedItems) {
    await this.set(this.CACHE_KEYS.EQUIPPED_ITEMS, equippedItems);
  }

  /**
   * Get cached equipped items
   * @returns {Promise<Object|null>} Cached equipped items or null
   */
  async getEquippedItems() {
    return await this.get(this.CACHE_KEYS.EQUIPPED_ITEMS, this.TTL.EQUIPPED_ITEMS);
  }

  /**
   * Get cache age (for debugging)
   * @param {string} key - Cache key
   * @returns {Promise<number|null>} Cache age in milliseconds or null
   */
  async getCacheAge(key) {
    try {
      const cached = await AsyncStorage.getItem(key);
      if (!cached) return null;

      const cacheEntry = JSON.parse(cached);
      return Date.now() - cacheEntry.timestamp;
    } catch (error) {
      return null;
    }
  }

  /**
   * Get cache statistics (for debugging)
   * @returns {Promise<Object>} Cache stats
   */
  async getStats() {
    const stats = {};
    
    for (const [name, key] of Object.entries(this.CACHE_KEYS)) {
      const age = await this.getCacheAge(key);
      const ttl = this.TTL[name];
      stats[name] = {
        exists: age !== null,
        age: age,
        ttl: ttl,
        fresh: age !== null && age < ttl,
      };
    }
    
    return stats;
  }
}

// Export singleton instance
export default new CacheService();

