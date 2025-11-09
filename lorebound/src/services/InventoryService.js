/**
 * Inventory Service
 * Handles API calls for user inventory and item management
 */

import { API_BASE_URL } from '../config/config';
import AuthUtils from './authUtils';
import CacheService from './CacheService';

class InventoryService {
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
   * Get user's complete inventory (with caching)
   * @param {boolean} forceRefresh - Force refresh from backend, skip cache
   * @returns {Promise<Object>} Inventory data with items, equipped items, and stats
   */
  async getInventory(forceRefresh = false) {
    // Try cache first unless force refresh
    if (!forceRefresh) {
      const cached = await CacheService.getInventory();
      if (cached) {
        console.log('[InventoryService] Using cached inventory');
        return cached;
      }
    }

    // Fetch from backend
    return await AuthUtils.authenticatedRequest(async (token) => {
      try {
        console.log('[InventoryService] Fetching inventory from backend');
        
        const response = await this.fetchWithTimeout(`${this.baseURL}/v1/inventory/`, {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        const responseText = await response.text();
        
        let data;
        try {
          data = JSON.parse(responseText);
        } catch (parseError) {
          console.error('[InventoryService] JSON parse error:', parseError);
          throw new Error(`Failed to parse inventory response: ${parseError.message}`);
        }

        if (!response.ok) {
          throw new Error(data?.detail || 'Failed to get inventory');
        }

        // Validate response structure
        if (!data || typeof data !== 'object') {
          throw new Error('Invalid inventory response');
        }

        // Cache the fresh data
        await CacheService.setInventory(data);
        await CacheService.setEquippedItems(data.equipped_items);
        
        console.log('[InventoryService] Inventory fetched and cached');
        return data;
      } catch (error) {
        console.error('[InventoryService] Get inventory error:', error.message);
        throw error;
      }
    });
  }

  /**
   * Equip an item
   * @param {string} itemId - UUID of the item to equip
   * @param {string} slot - Equipment slot (helmet, armor, weapon, shield)
   * @returns {Promise<Object>} Updated inventory data
   */
  async equipItem(itemId, slot) {
    const result = await AuthUtils.authenticatedRequest(async (token) => {
      try {
        console.log('[InventoryService] Equipping item:', itemId, 'in slot:', slot);
        
        const response = await this.fetchWithTimeout(`${this.baseURL}/v1/inventory/equip`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            item_id: itemId,
            slot: slot,
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          throw new Error(data.detail || 'Failed to equip item');
        }

        console.log('[InventoryService] Item equipped successfully');
        return data;
      } catch (error) {
        console.error('[InventoryService] Equip item error:', error);
        throw error;
      }
    });

    // Invalidate cache and update with fresh data
    await CacheService.setInventory(result);
    await CacheService.setEquippedItems(result.equipped_items);
    console.log('[InventoryService] Cache updated after equip');
    
    return result;
  }

  /**
   * Get items by slot from inventory
   * @param {Array} inventoryItems - Array of inventory items
   * @param {string} slot - Equipment slot (helmet, armor, weapon, shield)
   * @returns {Array} Items for that slot
   */
  getItemsBySlot(inventoryItems, slot) {
    return inventoryItems.filter(invItem => invItem.item.slot === slot);
  }

  /**
   * Get equipped item for a slot
   * @param {Object} equippedItems - Dictionary of equipped items by slot
   * @param {string} slot - Equipment slot
   * @returns {Object|null} Equipped item or null
   */
  getEquippedItemForSlot(equippedItems, slot) {
    return equippedItems[slot] || null;
  }

  /**
   * Get rarity color
   * @param {string} rarity - Item rarity (common, rare, epic, legendary)
   * @returns {string} Color code
   */
  getRarityColor(rarity) {
    const colors = {
      common: '#9e9e9e',
      rare: '#4a90e2',
      epic: '#9c27b0',
      legendary: '#ffd700',
    };
    return colors[rarity?.toLowerCase()] || colors.common;
  }

  /**
   * Get rarity emoji
   * @param {string} rarity - Item rarity
   * @returns {string} Emoji representation
   */
  getRarityEmoji(rarity) {
    const emojis = {
      common: '⚪',
      rare: '🔵',
      epic: '🟣',
      legendary: '🟡',
    };
    return emojis[rarity?.toLowerCase()] || '⚪';
  }
}

// Export singleton instance
export default new InventoryService();

