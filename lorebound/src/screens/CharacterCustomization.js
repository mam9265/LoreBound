import React, { useState, useEffect } from 'react';
import { View, Text, StyleSheet, Button, Image, TouchableOpacity, ScrollView, Alert } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import styles from '../styles/Styles';

function CharacterCustomization({ navigation }) {
  const [equipment, setEquipment] = useState({
    helmet: 'Leather Cap',
    armor: 'Traveler’s Tunic',
    weapon: 'Iron Sword',
    shield: 'Wooden Shield',
  });

  const [colorIndex, setColorIndex] = useState(0);

  const knightSprites = [
    require('../assets/RedKnight.png'),   // Red
    require('../assets/GreenKnight.png'), // Green
    require('../assets/BlueKnight.png'),  // Blue
  ];

  const colorNames = ['Red', 'Green', 'Blue'];

  const helmets = ['Leather Cap', 'Iron Helm', 'Mage Hood', 'Crown of Thorns'];
  const armors = ['Traveler’s Tunic', 'Chainmail', 'Mage Robe', 'Dark Plate'];
  const weapons = ['Iron Sword', 'Battle Axe', 'Magic Staff', 'Dagger'];
  const shields = ['Wooden Shield', 'Iron Shield', 'Magic Barrier', 'None'];

  const cycleOption = (key, options) => {
    const currentIndex = options.indexOf(equipment[key]);
    const nextIndex = (currentIndex + 1) % options.length;
    setEquipment({ ...equipment, [key]: options[nextIndex] });
  };

  const cycleColor = () => {
    setColorIndex((colorIndex + 1) % knightSprites.length);
  };

  const saveEquipment = async () => {
    try {
      const saveData = {
        equipment,
        colorIndex,
      };
      await AsyncStorage.setItem('characterData', JSON.stringify(saveData));
      Alert.alert('Saved!', 'Your character customization has been saved.');
    } catch (error) {
      console.error('Error saving character data:', error);
      Alert.alert('Error', 'Failed to save your customization.');
    }
  };

  useEffect(() => {
    const loadSavedData = async () => {
      try {
        const savedData = await AsyncStorage.getItem('characterData');
        if (savedData) {
          const parsed = JSON.parse(savedData);
          setEquipment(parsed.equipment || equipment);
          setColorIndex(parsed.colorIndex || 0);
        }
      } catch (error) {
        console.error('Error loading saved character data:', error);
      }
    };

    loadSavedData();
  }, []);

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <View style={styles.characterContainer}>
        <Text style={styles.header}>Character Equipment</Text>

        <View style={styles.previewContainer}>
          <Image
            source={knightSprites[colorIndex]}
            style={styles.characterImage}
            resizeMode="contain"
          />
          <Text style={styles.previewText}>{colorNames[colorIndex]} Knight</Text>
          <Text style={styles.equipmentText}>🪖 {equipment.helmet}</Text>
          <Text style={styles.equipmentText}>🧥 {equipment.armor}</Text>
          <Text style={styles.equipmentText}>⚔️ {equipment.weapon}</Text>
          <Text style={styles.equipmentText}>🛡️ {equipment.shield}</Text>
        </View>

        <View style={styles.buttonWrapper}>
          <Button title="Change Color" onPress={cycleColor} color="#0066FF" />
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

        <TouchableOpacity style={styles.saveButton} onPress={saveEquipment}>
          <Text style={styles.saveText}>Save Equipment</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.playButton, { backgroundColor: '#19376d', marginTop: 10 }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.playText}>BACK</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

export default CharacterCustomization;
