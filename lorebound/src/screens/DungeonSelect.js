import React from 'react';
import { View, Text, TouchableOpacity, Image, ScrollView } from 'react-native';
import styles from '../styles/Styles';

function DungeonSelect({ navigation}) {
  const dungeons = [
    { name: "Sports Dungeon", floors: "26/30" },
    { name: "Music Dungeon", floors: "15/30" },
    { name: "History Dungeon", floors: "2/30" },
    { name: "Book Dungeon", floors: "20/30" },
    { name: "Pop Culture Dungeon", floors: "12/30" },
    { name: "All Around Dungeon", floors: "9/30" },
  ];

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Dungeon Select</Text>
      <View style={styles.grid}>
        {dungeons.map((dungeon, index) => (
          <TouchableOpacity key={index} style={styles.dungeonButton}>
            <Text style={styles.dungeonTitle}>{dungeon.name}</Text>
            <Text style={styles.dungeonFloors}>Floors Cleared: {dungeon.floors}</Text>
          </TouchableOpacity>
        ))}
      </View>
    </ScrollView>
  );
}

export default DungeonSelect;