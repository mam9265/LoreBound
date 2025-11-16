import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
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
    <View style={[styles.container, { padding: 10 }]}>

      {/* 🔙 Back Button + Title Row */}
      <View
        style={{
          flexDirection: "row",
          alignItems: "center",
          marginBottom: 10,
        }}
      >
        <TouchableOpacity
          onPress={() => navigation.navigate("MainMenu")}
          style={{
            backgroundColor: "#19376d",
            paddingVertical: 6,
            paddingHorizontal: 14,
            borderRadius: 10,
            marginRight: 10
          }}
        >
          <Text style={{ color: "white", fontSize: 16 }}>Back</Text>
        </TouchableOpacity>

        <Text style={[styles.title, { flex: 1, textAlign: "center" }]}>
          Dungeon Select
        </Text>
      </View>

      {/* Grid that fits all buttons on screen */}
      <View
        style={{
          flex: 1,
          flexDirection: "row",
          flexWrap: "wrap",
          justifyContent: "space-between",
          alignContent: "flex-start",
          paddingTop: 5
        }}
      >
        {dungeons.map((dungeon) => (
          <TouchableOpacity
            key={dungeon.id}
            style={{
              width: "47%",            
              height: "50%",
              backgroundColor: "#0b2b5c",
              borderRadius: 20,
              padding: 12,
              marginBottom: 16,        
              justifyContent: "center",
              alignItems: "center",
            }}
            onPress={() => handleDungeonPress(dungeon)}
          >
            <Text style={{ fontSize: 28, marginBottom: 4 }}>
              {ContentService.getCategoryIcon(dungeon.category)}
            </Text>

            <Text style={[styles.dungeonTitle, { fontSize: 16 }]} numberOfLines={2}>
              {dungeon.title}
            </Text>

            <Text style={[styles.dungeonFloors, { fontSize: 14 }]}>
              {ContentService.getCategoryDisplayName(dungeon.category)}
            </Text>

            <Text style={[styles.dungeonFloors, { fontSize: 14 }]}>
              {dungeon.tiers?.length || 0} Tiers
            </Text>
          </TouchableOpacity>
        ))}
      </View>

    </View>
  );
}

export default DungeonSelect;
