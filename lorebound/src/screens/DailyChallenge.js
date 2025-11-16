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

      if (!forceRefresh) {
        const cached = await CacheService.get('cache_daily_challenge', 60 * 60 * 1000);
        if (cached) {
          setChallenge(cached);
          setLoadedFromCache(true);
          setIsLoading(false);
          return;
        }
      }

      const data = await AuthUtils.authenticatedRequest(async (token) => {
        const response = await fetch(`${API_BASE_URL}/v1/content/daily`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });

        if (!response.ok) {
          if (response.status === 401) throw new Error('401 Unauthorized');
          throw new Error('Failed to load daily challenge');
        }

        return await response.json();
      });

      await CacheService.set('cache_daily_challenge', data);

      setChallenge(data);
      setLoadedFromCache(false);
    } catch (error) {
      console.error('[DailyChallenge] Error:', error);

      if (error.message.includes('401')) {
        Alert.alert(
          'Session Expired',
          'Please log in again.',
          [
            {
              text: 'OK',
              onPress: () => {
                AuthUtils.clearAuthData();
                navigation.reset({ index: 0, routes: [{ name: 'Auth' }] });
              },
            },
          ]
        );
      } else {
        Alert.alert('Error', 'Failed to load daily challenge. Try again.');
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
      CacheService.invalidate('cache_daily_challenge');
      loadDailyChallenge(true);
      return;
    }

    const hours = Math.floor(diff / (1000 * 60 * 60));
    const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
    setTimeRemaining(`${hours}h ${minutes}m`);
  };

  const handlePlayChallenge = async () => {
    if (!challenge || !challenge.dungeon) return;

    try {
      // Start daily challenge run with is_daily flag
      const run = await RunService.startDailyChallengeRun(
        challenge.dungeon.id,
        {
          device: 'mobile',
          version: '1.0.0',
          challenge_id: challenge.id,
        }
      );

      const questionsData = await AuthUtils.authenticatedRequest(async (token) => {
        const res = await fetch(
          `${API_BASE_URL}/v1/content/daily/${challenge.id}/questions`,
          {
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
          }
        );

        if (!res.ok) {
          if (res.status === 401) throw new Error('401 Unauthorized');
          const errorData = await res.json();
          throw new Error(errorData.detail || 'Failed to get challenge questions');
        }

        return await res.json();
      });

      // Normalize run response
      const normalizedRun = {
        ...run,
        id: run.run_id || run.id,
      };

      navigation.navigate('RunGameplay', {
        dungeonId: challenge.dungeon.id,
        dungeonName: challenge.modifiers?.theme || 'Daily Challenge',
        dungeonCategory: challenge.dungeon.category || 'daily_challenge',
        runData: normalizedRun,
        questions: questionsData.questions,
        isDailyChallenge: true,
        challengeModifiers: challenge.modifiers,
      });
    } catch (error) {
      console.error('Failed to start challenge:', error);

      if (error.message.includes('401')) {
        Alert.alert(
          'Session Expired',
          'Please log in again.',
          [
            {
              text: 'OK',
              onPress: () => {
                AuthUtils.clearAuthData();
                navigation.reset({ index: 0, routes: [{ name: 'Auth' }] });
              },
            },
          ]
        );
      } else {
        Alert.alert('Error', 'Failed to start. Try again.');
      }
    }
  };

  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator size="large" color="#19376d" />
        <Text style={{ marginTop: 20, fontSize: 18, fontWeight: 'bold', color: '#19376d' }}>
          Loading Daily Challenge...
        </Text>
      </View>
    );
  }

  if (!challenge) {
    return (
      <View style={styles.container}>
        <Text style={{ fontSize: 22, marginBottom: 20 }}>No challenge available</Text>
        <TouchableOpacity
          style={[dailyStyles.playButton, { backgroundColor: '#19376d' }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={dailyStyles.playButtonText}>BACK</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const xpMultiplier = challenge.modifiers?.xp_multiplier || 1;
  const pointsMultiplier = challenge.modifiers?.points_multiplier || 1;
  const theme = challenge.modifiers?.theme || 'Daily Challenge';
  const description = challenge.modifiers?.description || 'Complete today\'s challenge!';

  return (
    <View style={[styles.container, { paddingTop: 10 }]}>
      {/* Header */}
      <View style={dailyStyles.headerCard}>
        <Text style={dailyStyles.title}>🏆 DAILY CHALLENGE 🏆</Text>
        <Text style={dailyStyles.theme}>{theme}</Text>
        <Text style={dailyStyles.timer}>⏰ {timeRemaining} remaining</Text>
        {loadedFromCache && <Text style={dailyStyles.cacheIndicator}>⚡ Instant Load</Text>}
      </View>

      {/* Description */}
      <View style={dailyStyles.descriptionCard}>
        <Text style={dailyStyles.difficultyBadge}>HARD MODE</Text>
        <Text style={dailyStyles.description}>{description}</Text>
      </View>

      {/* Bonus */}
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

      {/* CTA */}
      <TouchableOpacity style={dailyStyles.playButton} onPress={handlePlayChallenge}>
        <Text style={dailyStyles.playButtonText}>START CHALLENGE</Text>
      </TouchableOpacity>

      <TouchableOpacity style={dailyStyles.backButton} onPress={() => navigation.goBack()}>
        <Text style={dailyStyles.backButtonText}>BACK</Text>
      </TouchableOpacity>
    </View>
  );
}

const dailyStyles = StyleSheet.create({
  headerCard: {
    backgroundColor: '#19376d',
    padding: 14,
    borderRadius: 12,
    marginBottom: 12,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#ffd700',
  },
  title: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#ffd700',
    marginBottom: 6,
    textAlign: 'center',
  },
  theme: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
    textAlign: 'center',
  },
  timer: {
    fontSize: 13,
    color: '#a0c1d1',
    fontWeight: '600',
  },
  cacheIndicator: {
    fontSize: 10,
    color: '#4caf50',
    marginTop: 4,
    fontStyle: 'italic',
  },
  descriptionCard: {
    backgroundColor: '#19376d',
    padding: 12,
    borderRadius: 10,
    marginBottom: 15,
    alignItems: 'center',
  },
  difficultyBadge: {
    backgroundColor: '#ff4444',
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
    paddingHorizontal: 12,
    paddingVertical: 4,
    borderRadius: 12,
    marginBottom: 6,
  },
  description: {
    fontSize: 13,
    color: '#a0c1d1',
    textAlign: 'center',
    lineHeight: 18,
  },
  bonusCard: {
    backgroundColor: '#19376d',
    padding: 14,
    borderRadius: 10,
    marginBottom: 20,
    borderWidth: 2,
    borderColor: '#4caf50',
  },
  bonusTitle: {
    fontSize: 15,
    fontWeight: 'bold',
    color: '#4caf50',
    textAlign: 'center',
    marginBottom: 10,
  },
  bonusRow: {
    flexDirection: 'row',
    justifyContent: 'space-around',
  },
  bonusItem: {
    alignItems: 'center',
  },
  bonusValue: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#ffd700',
    marginBottom: 3,
  },
  bonusLabel: {
    fontSize: 12,
    color: '#a0c1d1',
    fontWeight: '600',
  },
  playButton: {
    backgroundColor: '#ffd700',
    paddingVertical: 12,
    paddingHorizontal: 30,
    borderRadius: 10,
    marginBottom: 10,
    elevation: 6,
  },
  playButtonText: {
    color: '#0b2447',
    fontSize: 16,
    fontWeight: 'bold',
    textAlign: 'center',
  },
  backButton: {
    backgroundColor: '#0b2447',
    paddingVertical: 10,
    paddingHorizontal: 20,
  },
  backButtonText: {
    color: '#a0c1d1',
    fontSize: 14,
    fontWeight: 'bold',
    textAlign: 'center',
  },
});

export default DailyChallenge;
