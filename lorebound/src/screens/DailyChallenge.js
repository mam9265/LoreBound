import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator, StyleSheet, Alert } from 'react-native';
import { API_BASE_URL } from '../config/config';
import AuthUtils from '../services/authUtils';
import { RunService, CacheService } from '../services';
import styles from '../styles/Styles';

function DailyChallenge({ navigation }) {
  const [challenge, setChallenge] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [timeRemaining, setTimeRemaining] = useState('');
  const [loadedFromCache, setLoadedFromCache] = useState(false);

  useEffect(() => {
    loadDailyChallenge();
    
    // Update time remaining every minute
    const interval = setInterval(updateTimeRemaining, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (challenge) {
      updateTimeRemaining();
    }
  }, [challenge]);

  const loadDailyChallenge = async (forceRefresh = false) => {
    try {
      setIsLoading(true);
      
      // Try cache first (unless force refresh)
      if (!forceRefresh) {
        const cached = await CacheService.get('cache_daily_challenge', 60 * 60 * 1000); // 1 hour TTL
        if (cached) {
          console.log('[DailyChallenge] Using cached daily challenge');
          setChallenge(cached);
          setLoadedFromCache(true);
          setIsLoading(false);
          return;
        }
      }
      
      console.log('[DailyChallenge] Fetching daily challenge from backend');
      const data = await AuthUtils.authenticatedRequest(async (token) => {
        const response = await fetch(`${API_BASE_URL}/v1/content/daily`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          if (response.status === 401) {
            throw new Error('401 Unauthorized');
          }
          throw new Error('Failed to load daily challenge');
        }

        return await response.json();
      });
      
      // Cache the daily challenge
      await CacheService.set('cache_daily_challenge', data);
      console.log('[DailyChallenge] Daily challenge fetched and cached');
      
      setChallenge(data);
      setLoadedFromCache(false);
    } catch (error) {
      console.error('[DailyChallenge] Failed to load daily challenge:', error);
      
      if (error.message.includes('401') || error.message.includes('Authentication failed')) {
        Alert.alert(
          'Session Expired',
          'Your session has expired. Please log in again.',
          [
            {
              text: 'OK',
              onPress: () => {
                AuthUtils.clearAuthData();
                navigation.reset({
                  index: 0,
                  routes: [{ name: 'Auth' }],
                });
              },
            },
          ]
        );
      } else {
        Alert.alert('Error', 'Failed to load daily challenge. Please try again.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const updateTimeRemaining = () => {
    if (!challenge?.expires_at) return;
    
    const now = new Date();
    const expires = new Date(challenge.expires_at);
    const diff = expires - now;
    
    if (diff <= 0) {
      setTimeRemaining('Expired - Refreshing...');
      // Invalidate cache and force refresh
      CacheService.invalidate('cache_daily_challenge');
      loadDailyChallenge(true); // Force refresh to get new challenge
      return;
    }
    
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    setTimeRemaining(`${hours}h ${minutes}m`);
  };

  const handlePlayChallenge = async () => {
    if (!challenge || !challenge.dungeon) return;
    
    try {
      // Start a run for the daily challenge dungeon
      const run = await RunService.startRun(challenge.dungeon.id, 1, {
        device: 'mobile',
        version: '1.0.0',
        is_daily_challenge: true,
        challenge_id: challenge.id,
      });
      
      // Get questions for the daily challenge
      const questionsData = await AuthUtils.authenticatedRequest(async (token) => {
        const questionsResponse = await fetch(
          `${API_BASE_URL}/v1/content/daily/${challenge.id}/questions`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );
        
        if (!questionsResponse.ok) {
          if (questionsResponse.status === 401) {
            throw new Error('401 Unauthorized');
          }
          throw new Error('Failed to get challenge questions');
        }
        
        return await questionsResponse.json();
      });
      
      // Navigate to gameplay with daily challenge modifiers
      navigation.navigate('RunGameplay', {
        dungeonId: challenge.dungeon.id,
        dungeonName: challenge.modifiers?.theme || 'Daily Challenge',
        dungeonCategory: challenge.dungeon.category || 'daily_challenge',
        runData: run,
        questions: questionsData.questions,
        isDailyChallenge: true,
        challengeModifiers: challenge.modifiers,
      });
    } catch (error) {
      console.error('Failed to start daily challenge:', error);
      
      if (error.message.includes('401') || error.message.includes('Authentication failed')) {
        Alert.alert(
          'Session Expired',
          'Your session has expired. Please log in again.',
          [
            {
              text: 'OK',
              onPress: () => {
                AuthUtils.clearAuthData();
                navigation.reset({
                  index: 0,
                  routes: [{ name: 'Auth' }],
                });
              },
            },
          ]
        );
      } else {
        Alert.alert('Error', 'Failed to start daily challenge. Please try again.');
      }
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator size="large" color="#19376d" />
        <Text style={[styles.headerText, { marginTop: 20 }]}>
          Loading Daily Challenge...
        </Text>
      </View>
    );
  }

  if (!challenge) {
    return (
      <View style={styles.container}>
        <Text style={styles.headerText}>No challenge available</Text>
        <TouchableOpacity
          style={[styles.playButton, { backgroundColor: '#19376d' }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.playText}>BACK</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const xpMultiplier = challenge.modifiers?.xp_multiplier || 1;
  const pointsMultiplier = challenge.modifiers?.points_multiplier || 1;
  const theme = challenge.modifiers?.theme || 'Daily Challenge';
  const description = challenge.modifiers?.description || 'Complete today\'s challenge!';

  return (
    <View style={styles.container}>
      <View style={dailyStyles.headerCard}>
        <Text style={dailyStyles.title}>🏆 DAILY CHALLENGE 🏆</Text>
        <Text style={dailyStyles.theme}>{theme}</Text>
        <Text style={dailyStyles.timer}>⏰ {timeRemaining} remaining</Text>
        {loadedFromCache && (
          <Text style={dailyStyles.cacheIndicator}>⚡ Instant Load</Text>
        )}
      </View>

      <View style={dailyStyles.descriptionCard}>
        <Text style={dailyStyles.difficultyBadge}>HARD MODE</Text>
        <Text style={dailyStyles.description}>{description}</Text>
      </View>

      <View style={dailyStyles.bonusCard}>
        <Text style={dailyStyles.bonusTitle}>BONUS REWARDS</Text>
        <View style={dailyStyles.bonusRow}>
          <View style={dailyStyles.bonusItem}>
            <Text style={dailyStyles.bonusValue}>{xpMultiplier}x</Text>
            <Text style={dailyStyles.bonusLabel}>XP</Text>
          </View>
          <View style={dailyStyles.bonusItem}>
            <Text style={dailyStyles.bonusValue}>{pointsMultiplier}x</Text>
            <Text style={dailyStyles.bonusLabel}>Points</Text>
          </View>
        </View>
      </View>

      <TouchableOpacity 
        style={dailyStyles.playButton}
        onPress={handlePlayChallenge}
      >
        <Text style={dailyStyles.playButtonText}>START CHALLENGE</Text>
      </TouchableOpacity>

      <TouchableOpacity
        style={dailyStyles.backButton}
        onPress={() => navigation.goBack()}
      >
        <Text style={dailyStyles.backButtonText}>BACK</Text>
      </TouchableOpacity>
    </View>
  );
}

const dailyStyles = StyleSheet.create({
  headerCard: {
    backgroundColor: '#19376d',
    padding: 20,
    borderRadius: 15,
    marginBottom: 20,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#ffd700',
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffd700',
    marginBottom: 10,
    textAlign: 'center',
  },
  theme: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 5,
    textAlign: 'center',
  },
  timer: {
    fontSize: 16,
    color: '#a0c1d1',
    fontWeight: '600',
  },
  cacheIndicator: {
    fontSize: 11,
    color: '#4caf50',
    marginTop: 5,
    fontStyle: 'italic',
  },
  descriptionCard: {
    backgroundColor: '#19376d',
    padding: 15,
    borderRadius: 10,
    marginBottom: 20,
    alignItems: 'center',
  },
  difficultyBadge: {
    backgroundColor: '#ff4444',
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
    paddingHorizontal: 15,
    paddingVertical: 5,
    borderRadius: 15,
    marginBottom: 10,
  },
  description: {
    fontSize: 16,
    color: '#a0c1d1',
    textAlign: 'center',
    lineHeight: 22,
  },
  bonusCard: {
    backgroundColor: '#19376d',
    padding: 20,
    borderRadius: 10,
    marginBottom: 30,
    borderWidth: 2,
    borderColor: '#4caf50',
  },
  bonusTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#4caf50',
    textAlign: 'center',
    marginBottom: 15,
  },
  bonusRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  bonusItem: {
    alignItems: 'center',
  },
  bonusValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#ffd700',
    marginBottom: 5,
  },
  bonusLabel: {
    fontSize: 14,
    color: '#a0c1d1',
    fontWeight: '600',
  },
  playButton: {
    backgroundColor: '#ffd700',
    paddingVertical: 15,
    paddingHorizontal: 40,
    borderRadius: 10,
    marginBottom: 15,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 5,
    elevation: 8,
  },
  playButtonText: {
    color: '#0b2447',
    fontSize: 18,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  backButton: {
    backgroundColor: 'transparent',
    paddingVertical: 12,
    paddingHorizontal: 30,
  },
  backButtonText: {
    color: '#a0c1d1',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default DailyChallenge;