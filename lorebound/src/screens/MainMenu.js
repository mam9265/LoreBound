import React, { useEffect, useState } from 'react';
import { View, Text, TouchableOpacity, Image, StyleSheet } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';

// Import the same sprites used in gameplay
import RedKnight from '../assets/RedKnight.png';
import GreenKnight from '../assets/GreenKnight.png';
import BlueKnight from '../assets/BlueKnight.png';

function MainMenu({ navigation }) {
  const [playerSprite, setPlayerSprite] = useState(null);

  useEffect(() => {
    const loadAvatar = async () => {
      try {
        const charJson = await AsyncStorage.getItem('characterData');
        if (charJson) {
          const parsed = JSON.parse(charJson);
          if (typeof parsed.colorIndex === 'number') {
            const sprites = [RedKnight, GreenKnight, BlueKnight];
            const idx = Math.max(0, Math.min(parsed.colorIndex, sprites.length - 1));
            setPlayerSprite(sprites[idx]);
            return;
          }
          if (parsed.avatarUri) {
            setPlayerSprite({ uri: parsed.avatarUri });
            return;
          }
        }

        const saveJson = await AsyncStorage.getItem('saveData');
        if (saveJson) {
          const parsed = JSON.parse(saveJson);
          if (parsed.avatarUri) {
            setPlayerSprite({ uri: parsed.avatarUri });
            return;
          }
          if (parsed.avatar) {
            setPlayerSprite({ uri: parsed.avatar });
            return;
          }
        }
      } catch (err) {
        console.warn('Error loading avatar:', err);
      }
    };

    loadAvatar();
  }, []);

  return (
    <View style={styles.container}>
      {/* Game Title */}
      <Text style={styles.title}>
        <Text style={styles.lore}>Lore</Text>
        <Text style={styles.bound}>Bound</Text>
      </Text>

      {/* Split layout */}
      <View style={styles.menuLayout}>
        {/* Left Side - Buttons */}
        <View style={styles.leftPanel}>
          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.navigate('DungeonSelect')}
          >
            <Text style={styles.buttonText}>Dungeon Select</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.button}
            onPress={() => navigation.navigate('DailyChallenge')}
          >
            <Text style={styles.buttonText}>Daily Challenge</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={styles.smallButton}
            onPress={() => navigation.navigate('Leaderboard')}
          >
            <Text style={styles.buttonText}>Leaderboards</Text>
          </TouchableOpacity>
        </View>

        {/* Right Side - Avatar & Customization */}
        <View style={styles.rightPanel}>
          {playerSprite ? (
            <Image
              source={playerSprite}
              style={styles.avatar}
            />
          ) : (
            <View style={styles.avatarPlaceholder}>
              <Text style={{ color: '#fff' }}>No Avatar</Text>
            </View>
          )}

          <TouchableOpacity
            style={styles.smallButton}
            onPress={() => navigation.navigate('CharacterCustomization')}
          >
            <Text style={styles.buttonText}>Customization</Text>
          </TouchableOpacity>
        </View>
      </View>
    </View>
  );
}

export default MainMenu;

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#A6D8E7',
    alignItems: 'center',
    justifyContent: 'flex-start',
    paddingVertical: 20,
  },
  title: {
    fontSize: 56,
    fontWeight: 'bold',
    marginTop: 0,
    marginBottom: 10,
  },
  lore: {
    color: '#FFFFFF',
  },
  bound: {
    color: '#0D1B52',
  },
  menuLayout: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    flex: 1,
    width: '90%',
    marginTop: 20,
  },
  leftPanel: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rightPanel: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  button: {
    backgroundColor: '#0D1B52',
    borderRadius: 20,
    paddingVertical: 22,
    paddingHorizontal: 45,
    width: 340,
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 25,
  },
  smallButton: {
    backgroundColor: '#4C63FF',
    borderRadius: 20,
    paddingVertical: 22,
    paddingHorizontal: 45,
    width: 340, // ← match width
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 25,
  },
  buttonText: {
    color: '#FFFFFF',
    fontSize: 24,
    fontFamily: 'serif',
    fontWeight: '600',
    textTransform: 'capitalize',
  },
  avatar: {
    width: 180,
    height: 180,
    resizeMode: 'contain',
    marginBottom: 20,
  },
  avatarPlaceholder: {
    width: 150,
    height: 150,
    borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: 20,
  },
});
