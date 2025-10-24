import React from 'react';
import { View, Text, TouchableOpacity, Image, ScrollView } from 'react-native';
import styles from '../styles/Styles';
import SportDungeon from './SportDungeon';
import MusicDungeon from './MusicDungeon';
import HistoryDungeon from './HistoryDungeon';
import BookDungeon from './BookDungeon';
import PopCultureDungeon from './PopCultureDungeon';
import AllAroundDungeon from './AllAroundDungeon';

function DungeonSelect({ navigation}) {
  const dungeons = [
    { name: "Sports Dungeon", floors: "26/30", route: "SportDungeon" },
    { name: "Music Dungeon", floors: "15/30", route: "MusicDungeon" },
    { name: "History Dungeon", floors: "2/30", route: "HistoryDungeon" },
    { name: "Book Dungeon", floors: "20/30", route: "BookDungeon" },
    { name: "Pop Culture Dungeon", floors: "12/30", route: "PopCultureDungeon" },
    { name: "All Around Dungeon", floors: "9/30", route: "AllAroundDungeon" },
  ];

  return (
    <ScrollView contentContainerStyle={styles.container}>
      <Text style={styles.title}>Dungeon Select</Text>
      <View style={styles.grid}>
        {dungeons.map((dungeon, index) => (
          <TouchableOpacity key={index} style={styles.dungeonButton} onPress={() => navigation.navigate(dungeon.route)}>
            <Text style={styles.dungeonTitle}>{dungeon.name}</Text>
            <Text style={styles.dungeonFloors}>Floors Cleared: {dungeon.floors}</Text>
          </TouchableOpacity>
        ))}
        <TouchableOpacity
          style={styles.smallButton}
          onPress={() => navigation.navigate('MainMenu')}
        >
          <Text style={styles.dungeonFloors}>Back to Home</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

export default DungeonSelect;
