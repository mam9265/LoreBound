import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Button, Image, TouchableOpacity, ScrollView, Alert, ActivityIndicator, Modal } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import styles from '../styles/Styles';
import { ProfileService, InventoryService } from '../services';

function CharacterCustomization({ navigation }) {
  const [inventory, setInventory] = useState(null);
  const [equippedItems, setEquippedItems] = useState({});
  const [colorIndex, setColorIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [modalVisible, setModalVisible] = useState(false);

  const knightSprites = [
    require('../assets/RedKnight.png'),   // Red
    require('../assets/GreenKnight.png'), // Green
    require('../assets/BlueKnight.png'),  // Blue
  ];

  const colorNames = ['Red', 'Green', 'Blue'];

  const cycleColor = () => {
    setColorIndex((colorIndex + 1) % knightSprites.length);
  };

  const equipItem = async (itemId, itemName, itemSlot) => {
    setSaving(true);
    try {
      console.log('[CharacterCustomization] Equipping item:', itemId, itemName, 'in slot:', itemSlot);
      console.log('[CharacterCustomization] Current saving state:', saving);
      
      const updatedInventory = await InventoryService.equipItem(itemId, itemSlot);
      console.log('[CharacterCustomization] Item equipped, response:', updatedInventory);
      
      setInventory(updatedInventory);
      setEquippedItems(updatedInventory.equipped_items);
      
      console.log(`[CharacterCustomization] ${itemName} equipped successfully`);
      // Don't show alert in modal, just update silently
    } catch (error) {
      console.error('[CharacterCustomization] Error equipping item:', error);
      console.error('[CharacterCustomization] Error details:', error.message);
      Alert.alert('Error', `Failed to equip ${itemName}.\n\n${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  const handleSaveAndClose = () => {
    setModalVisible(false);
    Alert.alert('Saved!', 'Your equipment has been saved!');
  };

  const saveColorChoice = async () => {
    setSaving(true);
    try {
      console.log('[CharacterCustomization] Saving color:', colorIndex);
      
      // Save color to profile (backend)
      const result = await ProfileService.updateCharacterCustomization({ colorIndex });
      console.log('[CharacterCustomization] Color saved to backend:', result);
      
      // Also save to local storage in multiple formats for compatibility
      await AsyncStorage.setItem('characterColorIndex', JSON.stringify(colorIndex));
      
      // Update characterData as well so MainMenu/RunGameplay can use it
      const currentCharData = await AsyncStorage.getItem('characterData');
      const charData = currentCharData ? JSON.parse(currentCharData) : {};
      charData.colorIndex = colorIndex;
      await AsyncStorage.setItem('characterData', JSON.stringify(charData));
      
      console.log('[CharacterCustomization] Color saved to local storage');
      
      Alert.alert('Saved!', `Your ${colorNames[colorIndex]} knight color has been saved!`);
    } catch (error) {
      console.error('[CharacterCustomization] Error saving color:', error);
      console.error('[CharacterCustomization] Error details:', error.message);
      Alert.alert('Error', `Failed to save color choice.\n\n${error.message}`);
    } finally {
      setSaving(false);
    }
  };

  useEffect(() => {
    const loadInventoryData = async () => {
      setLoading(true);
      try {
        console.log('[CharacterCustomization] Loading inventory...');
        
        // Load inventory from backend
        const inventoryData = await InventoryService.getInventory();
        console.log('[CharacterCustomization] Inventory loaded:', inventoryData);
        
        // Handle null or invalid response
        if (!inventoryData || typeof inventoryData !== 'object') {
          throw new Error('Invalid inventory data received from server');
        }
        
        setInventory(inventoryData);
        setEquippedItems(inventoryData.equipped_items || {});
        
        // Load color preference
        try {
          const profileData = await ProfileService.loadCharacterCustomization();
          if (profileData && profileData.colorIndex !== undefined) {
            setColorIndex(profileData.colorIndex);
          } else {
            // Try local storage
            const localColor = await AsyncStorage.getItem('characterColorIndex');
            if (localColor) {
              setColorIndex(JSON.parse(localColor));
            }
          }
        } catch (colorError) {
          console.warn('[CharacterCustomization] Could not load color, using default:', colorError);
          // Not critical, use default color
        }
        
        console.log('[CharacterCustomization] Loaded inventory and character data from backend');
      } catch (error) {
        console.error('[CharacterCustomization] Error loading inventory:', error);
        console.error('[CharacterCustomization] Error details:', error.message, error.stack);
        Alert.alert(
          'Error', 
          `Failed to load your inventory. Please try again.\n\nError: ${error.message}`,
          [
            { text: 'Retry', onPress: () => { setLoading(false); setTimeout(() => loadInventoryData(), 100); } },
            { text: 'Cancel', onPress: () => navigation.goBack() }
          ]
        );
      } finally {
        setLoading(false);
      }
    };

    loadInventoryData();
  }, []);

  if (loading) {
    return (
      <View style={[styles.characterContainer, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#0066FF" />
        <Text style={styles.previewText}>Loading character data...</Text>
      </View>
    );
  }

  // Safety check - if inventory failed to load
  if (!inventory) {
    return (
      <View style={[styles.characterContainer, { justifyContent: 'center', alignItems: 'center' }]}>
        <Text style={styles.header}>⚠️ Inventory Not Available</Text>
        <Text style={styles.previewText}>Unable to load inventory data</Text>
        <TouchableOpacity
          style={[styles.playButton, { marginTop: 20 }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.playText}>GO BACK</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const renderItemSlot = (slotName, slotKey, emoji) => {
    if (!inventory || !inventory.items) {
      return (
        <View style={customStyles.slotSection} key={slotKey}>
          <Text style={customStyles.slotTitle}>{emoji} {slotName}</Text>
          <Text style={customStyles.equippedLabel}>No items available</Text>
        </View>
      );
    }

    const slotItems = InventoryService.getItemsBySlot(inventory.items, slotKey);
    const equippedItem = equippedItems[slotKey];
    
    console.log(`[CharacterCustomization] Rendering ${slotKey} slot with ${slotItems.length} items`);

    return (
      <View style={customStyles.slotSection} key={slotKey}>
        <Text style={customStyles.slotTitle}>{emoji} {slotName}</Text>
        <Text style={customStyles.equippedLabel}>
          Equipped: {equippedItem ? equippedItem.name : 'None'}
          {equippedItem && (
            <Text style={[customStyles.rarityBadge, { color: InventoryService.getRarityColor(equippedItem.rarity) }]}>
              {' '}{InventoryService.getRarityEmoji(equippedItem.rarity)} {equippedItem.rarity.toUpperCase()}
            </Text>
          )}
        </Text>
        
        {slotItems.length === 0 ? (
          <Text style={customStyles.noItemsText}>No items in this slot yet</Text>
        ) : (
          <ScrollView horizontal showsHorizontalScrollIndicator={false} style={customStyles.itemScroll}>
            {slotItems.map((invItem) => {
              const item = invItem.item;
              const isEquipped = invItem.equipped;
              
              return (
                <TouchableOpacity
                  key={item.id}
                  style={[
                    customStyles.itemCard,
                    isEquipped && customStyles.itemCardEquipped,
                    { borderColor: InventoryService.getRarityColor(item.rarity) }
                  ]}
                  onPress={() => {
                    console.log('[CharacterCustomization] Item tapped:', item.name, 'slot:', item.slot, 'isEquipped:', isEquipped, 'saving:', saving);
                    if (!isEquipped && !saving) {
                      equipItem(item.id, item.name, item.slot);
                    } else {
                      console.log('[CharacterCustomization] Tap ignored - item already equipped or saving');
                    }
                  }}
                  disabled={saving}
                  activeOpacity={isEquipped ? 1 : 0.7}
                >
                  <Text style={[
                    customStyles.itemRarity,
                    { color: InventoryService.getRarityColor(item.rarity) }
                  ]}>
                    {InventoryService.getRarityEmoji(item.rarity)} {item.rarity.toUpperCase()}
                  </Text>
                  <Text style={customStyles.itemName} numberOfLines={2}>
                    {item.name}
                  </Text>
                  {isEquipped ? (
                    <Text style={customStyles.equippedBadge}>✓ EQUIPPED</Text>
                  ) : (
                    <Text style={customStyles.tapToEquipText}>Tap to Equip</Text>
                  )}
                </TouchableOpacity>
              );
            })}
          </ScrollView>
        )}
      </View>
    );
  };

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <View style={styles.characterContainer}>
        <Text style={styles.header}>Character Equipment</Text>

        {/* Character Preview */}
        <View style={styles.previewContainer}>
          <TouchableOpacity onPress={() => setModalVisible(true)} activeOpacity={0.8}>
            <Image
              source={knightSprites[colorIndex]}
              style={styles.characterImage}
              resizeMode="contain"
            />
          </TouchableOpacity>
          <Text style={styles.previewText}>{colorNames[colorIndex]} Knight</Text>
          <Text style={[styles.previewText, { fontSize: 12, fontStyle: 'italic', marginTop: 4 }]}>Tap knight to equip items</Text>
          
          {/* Show equipped items */}
          <Text style={styles.equipmentText}>🪖 {equippedItems.helmet?.name || 'No Helmet'}</Text>
          <Text style={styles.equipmentText}>🧥 {equippedItems.armor?.name || 'No Armor'}</Text>
          <Text style={styles.equipmentText}>⚔️ {equippedItems.weapon?.name || 'No Weapon'}</Text>
          <Text style={styles.equipmentText}>🛡️ {equippedItems.shield?.name || 'No Shield'}</Text>

          {/* Total Stats */}
          {inventory && inventory.total_stats && typeof inventory.total_stats === 'object' && Object.keys(inventory.total_stats).length > 0 && (
            <View style={customStyles.statsContainer}>
              <Text style={customStyles.statsTitle}>Total Stats:</Text>
              {Object.entries(inventory.total_stats).map(([stat, value]) => (
                <Text key={stat} style={customStyles.statText}>
                  {stat}: +{typeof value === 'number' ? value.toFixed(2) : value}
                </Text>
              ))}
            </View>
          )}
        </View>

        {/* Color Selection */}
        <View style={styles.buttonWrapper}>
          <Button title="Change Color" onPress={cycleColor} color="#0066FF" />
          <TouchableOpacity 
            style={[customStyles.saveColorButton, saving && { opacity: 0.6 }]} 
            onPress={saveColorChoice}
            disabled={saving}
          >
            <Text style={customStyles.saveColorText}>Save Color</Text>
          </TouchableOpacity>
        </View>

        <TouchableOpacity
          style={[styles.playButton, { backgroundColor: '#19376d', marginTop: 20 }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.playText}>BACK</Text>
        </TouchableOpacity>
      </View>

      {/* Equipment Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setModalVisible(false)}
      >
        <View style={customStyles.modalOverlay}>
          <View style={customStyles.modalContainer}>
            <View style={customStyles.modalHeader}>
              <Text style={customStyles.modalTitle}>Equip Items</Text>
              <TouchableOpacity
                onPress={() => setModalVisible(false)}
                style={customStyles.closeButton}
              >
                <Text style={customStyles.closeButtonText}>✕</Text>
              </TouchableOpacity>
            </View>

            <ScrollView 
              style={customStyles.modalContent}
              contentContainerStyle={customStyles.modalScrollContent}
            >
              {renderItemSlot('Helmets', 'helmet', '🪖')}
              {renderItemSlot('Armor', 'armor', '🧥')}
              {renderItemSlot('Weapons', 'weapon', '⚔️')}
              {renderItemSlot('Shields', 'shield', '🛡️')}
            </ScrollView>

            <View style={customStyles.modalFooter}>
              <TouchableOpacity
                style={[customStyles.saveButton, saving && { opacity: 0.6 }]}
                onPress={handleSaveAndClose}
                disabled={saving}
              >
                <Text style={customStyles.saveButtonText}>Save & Close</Text>
              </TouchableOpacity>
              <TouchableOpacity
                style={customStyles.cancelButton}
                onPress={() => setModalVisible(false)}
              >
                <Text style={customStyles.cancelButtonText}>Cancel</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const customStyles = StyleSheet.create({
  slotSection: {
    marginVertical: 8,
    backgroundColor: '#19376d',
    borderRadius: 8,
    padding: 12,
    maxHeight: 180, // Limit height to prevent taking whole screen
  },
  slotTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  equippedLabel: {
    color: '#a0c1d1',
    fontSize: 12,
    marginBottom: 8,
  },
  rarityBadge: {
    fontWeight: 'bold',
    fontSize: 11,
  },
  itemScroll: {
    maxHeight: 100,
  },
  itemCard: {
    width: 120,
    height: 90,
    backgroundColor: '#0b2447',
    borderRadius: 8,
    padding: 8,
    marginRight: 8,
    borderWidth: 3,
    alignItems: 'center',
    justifyContent: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.3,
    shadowRadius: 3,
    elevation: 3,
  },
  itemCardEquipped: {
    backgroundColor: '#1a4d2e',
    borderWidth: 3,
  },
  itemRarity: {
    fontSize: 9,
    fontWeight: 'bold',
    marginBottom: 2,
    textAlign: 'center',
  },
  itemName: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    textAlign: 'center',
    marginBottom: 2,
  },
  equippedBadge: {
    color: '#4caf50',
    fontSize: 9,
    fontWeight: 'bold',
    marginTop: 4,
  },
  tapToEquipText: {
    color: '#4a90e2',
    fontSize: 9,
    marginTop: 4,
    fontStyle: 'italic',
  },
  noItemsText: {
    color: '#888',
    fontSize: 12,
    fontStyle: 'italic',
    paddingVertical: 10,
  },
  statsContainer: {
    marginTop: 8,
    padding: 8,
    backgroundColor: '#0b2447',
    borderRadius: 6,
    maxHeight: 120,
  },
  statsTitle: {
    color: '#4a90e2',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 4,
  },
  statText: {
    color: '#a0c1d1',
    fontSize: 11,
  },
  saveColorButton: {
    backgroundColor: '#4a90e2',
    paddingVertical: 8,
    paddingHorizontal: 16,
    borderRadius: 6,
    marginLeft: 10,
  },
  saveColorText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.7)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  modalContainer: {
    width: '90%',
    maxWidth: 500,
    maxHeight: '85%',
    backgroundColor: '#0b2447',
    borderRadius: 16,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.5,
    shadowRadius: 8,
    elevation: 10,
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#19376d',
    borderBottomWidth: 2,
    borderBottomColor: '#4a90e2',
  },
  modalTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  closeButton: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#4a90e2',
    justifyContent: 'center',
    alignItems: 'center',
  },
  closeButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  modalContent: {
    flex: 1,
  },
  modalScrollContent: {
    padding: 16,
  },
  modalFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    padding: 16,
    backgroundColor: '#19376d',
    borderTopWidth: 2,
    borderTopColor: '#4a90e2',
  },
  saveButton: {
    flex: 1,
    backgroundColor: '#4a90e2',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginRight: 6,
  },
  saveButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  cancelButton: {
    flex: 1,
    backgroundColor: '#666',
    paddingVertical: 12,
    paddingHorizontal: 24,
    borderRadius: 8,
    alignItems: 'center',
    justifyContent: 'center',
    marginLeft: 6,
  },
  cancelButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});


export default CharacterCustomization;
