import React from 'react';
import { View, Text, StyleSheet, TouchableOpacity, ImageBackground, Image } from 'react-native';

export default function App() {
  const [name, setName] = React.useState('');

  return (
    <View style={styles.container}>
      {/* Title */}
      <Text style={styles.title}>
        <Text style={styles.lore}>Lore</Text>
        <Text style={styles.bound}>Bound</Text>
      </Text>
      {/* Buttons */}
      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Dungeon Select</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.button}>
        <Text style={styles.buttonText}>Daily Challenge</Text>
      </TouchableOpacity>

      <TouchableOpacity style={styles.smallButton}>
        <Text style={styles.buttonText}>Leaderboards</Text>
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
  buttonText: {
    color: '#ffffff',
    fontSize: 22,
    fontFamily: 'serif',
    textTransform: 'capitalize',
  },
});