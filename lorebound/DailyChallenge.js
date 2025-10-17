import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, Image } from 'react-native';

function DailyChallenge({ navigation  }) {
  return (
    <View style={styles.container}>
      <View style={styles.headerBox}>
        {/* Menu */}
        <Text style={styles.headerText}>Today’s Theme: Music</Text>
        <Text style={styles.headerSubText}>Time Until Next Challenge: 7 Hours</Text>
      </View>
      {/* Play Button */}
      <TouchableOpacity style={styles.playButton}>
        <Text style={styles.playText}>PLAY</Text>
      </TouchableOpacity>
      {/* Back Button */}
      <TouchableOpacity
        style={[styles.playButton, {backgroundColor: '#19376d', marginTop: 10 }]} onPress={() => navigation.goBack()}>
        <Text style={styles.playText}>BACK</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#a5d7e8',
  },
  title: {
    fontSize: 48,
    fontWeight: '600',
    marginBottom: 40,
    textAlign: 'center',
    color: '#19376d'
  },
  lore:{
    color: '#ffffff',
  },
  bound:{
    color: '#19376d',
  },
  button: {
    backgroundColor: '#19376d',
    paddingVertical: 16,
    paddingHorizontal: 50,
    borderRadius: 20,
    marginBottom: 20,
  },
  smallButton: {
    backgroundColor: '#5260e0',
    paddingVertical: 12,
    paddingHorizontal: 40,
    borderRadius: 20,
    marginBottom: 40,
  },
  DungeonButton: {
    backgroundColor: '#19376d',
    paddingVertical: 16,
    paddingHorizontal: 50,
    borderRadius: 20,
    marginBottom: 20,
  },
  DungeonSelectText: {
    color: '#ffffff',
    fontSize: 22,
    fontFamily: 'serif',
    textTransform: 'capitalize',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 22,
    fontFamily: 'serif',
    textTransform: 'capitalize',
  },
  headerBox: {
    backgroundColor: '#19376d',
    padding: 20,
    borderRadius: 4,
    marginBottom: 20,
  },
  headerText: {
    color: 'white',
    fontSize: 26,
    textAlign: 'center',
    fontFamily: 'serif',
  },
  headerSubText: {
    color: 'white',
    fontSize: 18,
    textAlign: 'center',
    marginTop: 5,
  },
  playButton: {
    backgroundColor: '#5260e0',
    marginTop: 10
  },
  playText: {
    color: 'white',
    fontSize: 20,
    fontFamily: 'serif',
  },
});