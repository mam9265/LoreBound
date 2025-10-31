import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  StyleSheet,
  ScrollView,
} from 'react-native';

// Simplified debug version of RunGameplay to find the issue

function RunGameplayDebug({ navigation, route }) {
  const [debugInfo, setDebugInfo] = useState({});
  const [error, setError] = useState(null);

  useEffect(() => {
    try {
      // Log what we receive
      console.log('=== RunGameplay Debug ===');
      console.log('Route params:', route?.params);
      
      const params = route?.params || {};
      setDebugInfo({
        hasDungeonId: !!params.dungeonId,
        hasName: !!params.dungeonName,
        hasCategory: !!params.dungeonCategory,
        dungeonId: params.dungeonId,
        dungeonName: params.dungeonName,
        dungeonCategory: params.dungeonCategory,
      });
    } catch (err) {
      console.error('Error in RunGameplay:', err);
      setError(err.message);
    }
  }, [route]);

  if (error) {
    return (
      <View style={styles.container}>
        <Text style={styles.errorText}>ERROR: {error}</Text>
        <TouchableOpacity 
          style={styles.button}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.buttonText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <ScrollView style={styles.container}>
      <Text style={styles.title}>RunGameplay Debug Screen</Text>
      
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Route Params Received:</Text>
        <Text style={styles.text}>
          Has Dungeon ID: {debugInfo.hasDungeonId ? '✅ Yes' : '❌ No'}
        </Text>
        <Text style={styles.text}>
          Has Name: {debugInfo.hasName ? '✅ Yes' : '❌ No'}
        </Text>
        <Text style={styles.text}>
          Has Category: {debugInfo.hasCategory ? '✅ Yes' : '❌ No'}
        </Text>
      </View>

      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Values:</Text>
        <Text style={styles.text}>ID: {debugInfo.dungeonId || 'Not provided'}</Text>
        <Text style={styles.text}>Name: {debugInfo.dungeonName || 'Not provided'}</Text>
        <Text style={styles.text}>Category: {debugInfo.dungeonCategory || 'Not provided'}</Text>
      </View>

      <TouchableOpacity 
        style={styles.button}
        onPress={() => navigation.goBack()}
      >
        <Text style={styles.buttonText}>Go Back</Text>
      </TouchableOpacity>

      <View style={styles.section}>
        <Text style={styles.infoText}>
          This is a debug screen. If you see this, the navigation is working!
        </Text>
        <Text style={styles.infoText}>
          Check Metro terminal for console.log output.
        </Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0b2447',
    padding: 20,
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 20,
    textAlign: 'center',
  },
  section: {
    backgroundColor: '#19376d',
    padding: 15,
    borderRadius: 10,
    marginBottom: 15,
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4a90e2',
    marginBottom: 10,
  },
  text: {
    fontSize: 16,
    color: '#fff',
    marginBottom: 5,
  },
  errorText: {
    fontSize: 18,
    color: '#ff4444',
    textAlign: 'center',
    marginBottom: 20,
  },
  infoText: {
    fontSize: 14,
    color: '#a0c1d1',
    marginTop: 5,
  },
  button: {
    backgroundColor: '#4a90e2',
    padding: 15,
    borderRadius: 10,
    alignItems: 'center',
    marginVertical: 10,
  },
  buttonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default RunGameplayDebug;

