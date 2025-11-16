import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ScrollView, ActivityIndicator, Alert } from 'react-native';
import styles from '../styles/Styles';
import { ContentService } from '../services';

function DungeonSelect({ navigation }) {
  const [dungeons, setDungeons] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDungeons();
  }, []);

  const loadDungeons = async () => {
    try {
      setIsLoading(true);
      const data = await ContentService.getDungeons();
      setDungeons(data);
    } catch (error) {
      console.error('Failed to load dungeons:', error);
      Alert.alert(
        'Error',
        'Failed to load dungeons. Please check your connection and try again.',
        [
          { text: 'Retry', onPress: loadDungeons },
          { text: 'Cancel', onPress: () => navigation.goBack() }
        ]
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleDungeonPress = (dungeon) => {
    // Navigate to RunGameplay with dungeon data
    navigation.navigate('RunGameplay', {
      dungeonId: dungeon.id,
      dungeonName: dungeon.title,
      dungeonCategory: dungeon.category,
    });
  };

  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center', alignItems: 'center' }]}>
        <ActivityIndicator size="large" color="#19376d" />
        <Text style={[styles.headerText, { marginTop: 20 }]}>Loading Dungeons...</Text>
      </View>
    );
  }

  return (
    <ScrollView contentContainerStyle={styles.scrollContainer}>
      <Text style={styles.title}>Dungeon Select</Text>
      <View style={styles.grid}>
        {dungeons.map((dungeon) => (
          <TouchableOpacity
            key={dungeon.id}
            style={styles.dungeonButton}
            onPress={() => handleDungeonPress(dungeon)}
          >
            <Text style={{ fontSize: 36, marginBottom: 8 }}>
              {ContentService.getCategoryIcon(dungeon.category)}
            </Text>
            <Text style={styles.dungeonTitle} numberOfLines={2} ellipsizeMode="tail">
              {dungeon.title}
            </Text>
            <Text style={styles.dungeonFloors}>
              {ContentService.getCategoryDisplayName(dungeon.category)}
            </Text>
            <Text style={styles.dungeonFloors}>
              {dungeon.tiers?.length || 0} Tiers
            </Text>
          </TouchableOpacity>
        ))}
        <TouchableOpacity
          style={[styles.smallButton, { flex: 1}]}
          onPress={() => navigation.navigate('MainMenu')}
        >
          <Text style={styles.dungeonFloors}>Back to Home</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

export default DungeonSelect;
