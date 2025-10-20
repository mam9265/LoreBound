import React, { useState } from 'react';
import { View, Text, StyleSheet, Button, Image, TouchableOpacity } from 'react-native';

const CharacterCustomization = () => {
  const [equipment, setEquipment] = useState({
    helmet: 'Leather Cap',
    armor: 'Traveler’s Tunic',
    weapon: 'Iron Sword',
    shield: 'Wooden Shield',
  });

  const helmets = ['Leather Cap', 'Iron Helm', 'Mage Hood', 'Crown of Thorns'];
  const armors = ['Traveler’s Tunic', 'Chainmail', 'Mage Robe', 'Dark Plate'];
  const weapons = ['Iron Sword', 'Battle Axe', 'Magic Staff', 'Dagger'];
  const shields = ['Wooden Shield', 'Iron Shield', 'Magic Barrier', 'None'];

  const cycleOption = (key, options) => {
    const currentIndex = options.indexOf(equipment[key]);
    const nextIndex = (currentIndex + 1) % options.length;
    setEquipment({ ...equipment, [key]: options[nextIndex] });
  };

  return (
    <View style={styles.container}>
      <Text style={styles.header}>Character Equipment</Text>

      <View style={styles.previewContainer}>
        {}
        <Image
          source={{ uri: 'https://loreboundplaceholder.com' }}
          style={styles.characterImage}
        />
        <Text style={styles.previewText}>Your Loadout</Text>
        <Text style={styles.equipmentText}>🪖 {equipment.helmet}</Text>
        <Text style={styles.equipmentText}>🧥 {equipment.armor}</Text>
        <Text style={styles.equipmentText}>⚔️ {equipment.weapon}</Text>
        <Text style={styles.equipmentText}>🛡️ {equipment.shield}</Text>
      </View>

      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>Helmet: {equipment.helmet}</Text>
        <Button title="Change Helmet" onPress={() => cycleOption('helmet', helmets)} />
      </View>

      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>Armor: {equipment.armor}</Text>
        <Button title="Change Armor" onPress={() => cycleOption('armor', armors)} />
      </View>

      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>Weapon: {equipment.weapon}</Text>
        <Button title="Change Weapon" onPress={() => cycleOption('weapon', weapons)} />
      </View>

      <View style={styles.optionGroup}>
        <Text style={styles.optionLabel}>Shield: {equipment.shield}</Text>
        <Button title="Change Shield" onPress={() => cycleOption('shield', shields)} />
      </View>

      <TouchableOpacity style={styles.saveButton}>
        <Text style={styles.saveText}>Save Equipment</Text>
      </TouchableOpacity>
    </View>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    padding: 20,
    backgroundColor: '#121212',
  },
  header: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  previewContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  characterImage: {
    width: 150,
    height: 150,
    borderRadius: 10,
    marginBottom: 10,
  },
  previewText: {
    color: '#aaa',
    fontSize: 16,
    marginBottom: 5,
  },
  equipmentText: {
    color: '#fff',
    fontSize: 16,
  },
  optionGroup: {
    marginVertical: 10,
  },
  optionLabel: {
    color: '#fff',
    fontSize: 18,
    marginBottom: 5,
  },
  saveButton: {
    marginTop: 30,
    backgroundColor: '#4e9bde',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  saveText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default CharacterEquipment;