import React from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import styles from '../styles/Styles';

function MainMenu({ navigation }) {
  return (
    <View style={styles.container}>
      {/* Title */}
      <Text style={styles.title}>
        <Text style={styles.lore}>Lore</Text>
        <Text style={styles.bound}>Bound</Text>
      </Text>
      {/* Buttons */}
      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('DungeonSelect')}>
        <Text style={styles.buttonText}>Dungeon Select</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('DailyChallenge')}>
        <Text style={styles.buttonText}>Daily Challenge</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.smallButton} onPress={() => navigation.navigate('Leaderboard')}>
        <Text style={styles.buttonText}>Leaderboards</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.button} onPress={() => navigation.navigate('CharacterCustomization')}>
        <Text style={styles.buttonText}>Character Customization</Text>
      </TouchableOpacity>

    </View>
  );
}

export default MainMenu;