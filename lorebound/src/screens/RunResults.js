import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ScrollView,
  StyleSheet,
} from 'react-native';
import styles from '../styles/Styles';

function RunResults({ navigation, route }) {
  const {
    runData,
    score,
    questionsAnswered,
    correctAnswers,
    maxStreak,
    dungeonName,
  } = route.params || {};

  const accuracy = questionsAnswered > 0
    ? Math.round((correctAnswers / questionsAnswered) * 100)
    : 0;

  const handleViewLeaderboard = () => {
    navigation.navigate('Leaderboard');
  };

  const handlePlayAgain = () => {
    navigation.popToTop();
    navigation.navigate('DungeonSelect');
  };

  const handleMainMenu = () => {
    navigation.popToTop();
    navigation.navigate('MainMenu');
  };

  const handleViewHistory = () => {
    navigation.navigate('RunHistory');
  };

  return (
    <ScrollView style={resultStyles.container}>
      <View style={resultStyles.content}>
        {/* Header */}
        <View style={resultStyles.header}>
          <Text style={resultStyles.title}>Run Complete!</Text>
          <Text style={resultStyles.subtitle}>{dungeonName}</Text>
        </View>

        {/* Score Card */}
        <View style={resultStyles.scoreCard}>
          <Text style={resultStyles.scoreLabel}>Final Score</Text>
          <Text style={resultStyles.scoreValue}>{score || runData?.total_score || 0}</Text>
          {runData?.rank && (
            <Text style={resultStyles.rankText}>Rank: #{runData.rank}</Text>
          )}
        </View>

        {/* Stats Grid */}
        <View style={resultStyles.statsGrid}>
          <View style={resultStyles.statBox}>
            <Text style={resultStyles.statValue}>{questionsAnswered}</Text>
            <Text style={resultStyles.statLabel}>Questions</Text>
          </View>

          <View style={resultStyles.statBox}>
            <Text style={resultStyles.statValue}>{correctAnswers}</Text>
            <Text style={resultStyles.statLabel}>Correct</Text>
          </View>

          <View style={resultStyles.statBox}>
            <Text style={[resultStyles.statValue, resultStyles.accuracyValue]}>
              {accuracy}%
            </Text>
            <Text style={resultStyles.statLabel}>Accuracy</Text>
          </View>

          <View style={resultStyles.statBox}>
            <Text style={resultStyles.statValue}>{maxStreak}🔥</Text>
            <Text style={resultStyles.statLabel}>Best Streak</Text>
          </View>
        </View>

        {/* Performance Message */}
        <View style={resultStyles.messageCard}>
          {accuracy >= 90 && (
            <>
              <Text style={resultStyles.messageTitle}>Legendary!</Text>
              <Text style={resultStyles.messageText}>
                Outstanding performance! You're a trivia master!
              </Text>
            </>
          )}
          {accuracy >= 75 && accuracy < 90 && (
            <>
              <Text style={resultStyles.messageTitle}>Excellent!</Text>
              <Text style={resultStyles.messageText}>
                Great job! You really know your stuff!
              </Text>
            </>
          )}
          {accuracy >= 60 && accuracy < 75 && (
            <>
              <Text style={resultStyles.messageTitle}>Well Done!</Text>
              <Text style={resultStyles.messageText}>
                Nice work! Keep practicing to improve even more!
              </Text>
            </>
          )}
          {accuracy < 60 && (
            <>
              <Text style={resultStyles.messageTitle}>Keep Trying!</Text>
              <Text style={resultStyles.messageText}>
                Every run makes you stronger. Try again!
              </Text>
            </>
          )}
        </View>

        {/* Rewards (placeholder for future implementation) */}
        <View style={resultStyles.rewardsCard}>
          <Text style={resultStyles.rewardsTitle}>Rewards Earned</Text>
          <View style={resultStyles.rewardsList}>
            <View style={resultStyles.rewardItem}>
              <Text style={resultStyles.rewardIcon}>⭐</Text>
              <Text style={resultStyles.rewardText}>
                {Math.floor(score / 10)} XP
              </Text>
            </View>
            {maxStreak >= 5 && (
              <View style={resultStyles.rewardItem}>
                <Text style={resultStyles.rewardIcon}>🔥</Text>
                <Text style={resultStyles.rewardText}>Streak Master Badge</Text>
              </View>
            )}
            {accuracy === 100 && (
              <View style={resultStyles.rewardItem}>
                <Text style={resultStyles.rewardIcon}>💯</Text>
                <Text style={resultStyles.rewardText}>Perfect Score!</Text>
              </View>
            )}
          </View>
        </View>

        {/* Action Buttons */}
        <View style={resultStyles.actionsContainer}>
          <TouchableOpacity
            style={[resultStyles.actionButton, resultStyles.primaryButton]}
            onPress={handlePlayAgain}
          >
            <Text style={resultStyles.primaryButtonText}>Play Again</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[resultStyles.actionButton, resultStyles.secondaryButton]}
            onPress={handleViewLeaderboard}
          >
            <Text style={resultStyles.secondaryButtonText}>View Leaderboard</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[resultStyles.actionButton, resultStyles.secondaryButton]}
            onPress={handleViewHistory}
          >
            <Text style={resultStyles.secondaryButtonText}>Run History</Text>
          </TouchableOpacity>

          <TouchableOpacity
            style={[resultStyles.actionButton, resultStyles.tertiaryButton]}
            onPress={handleMainMenu}
          >
            <Text style={resultStyles.tertiaryButtonText}>Main Menu</Text>
          </TouchableOpacity>
        </View>
      </View>
    </ScrollView>
  );
}

const resultStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0b2447',
  },
  content: {
    padding: 20,
  },
  header: {
    alignItems: 'center',
    marginBottom: 24,
    marginTop: 20,
  },
  title: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  subtitle: {
    fontSize: 18,
    color: '#a0c1d1',
  },
  scoreCard: {
    backgroundColor: '#19376d',
    borderRadius: 16,
    padding: 32,
    alignItems: 'center',
    marginBottom: 24,
    borderWidth: 2,
    borderColor: '#4a90e2',
  },
  scoreLabel: {
    fontSize: 16,
    color: '#a0c1d1',
    marginBottom: 8,
  },
  scoreValue: {
    fontSize: 56,
    fontWeight: 'bold',
    color: '#4a90e2',
  },
  rankText: {
    fontSize: 18,
    color: '#ffd700',
    marginTop: 12,
    fontWeight: 'bold',
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginBottom: 24,
  },
  statBox: {
    width: '48%',
    backgroundColor: '#19376d',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginBottom: 12,
  },
  statValue: {
    fontSize: 32,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 8,
  },
  accuracyValue: {
    color: '#4caf50',
  },
  statLabel: {
    fontSize: 14,
    color: '#a0c1d1',
  },
  messageCard: {
    backgroundColor: '#19376d',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
    alignItems: 'center',
  },
  messageTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#4a90e2',
    marginBottom: 8,
  },
  messageText: {
    fontSize: 16,
    color: '#a0c1d1',
    textAlign: 'center',
    lineHeight: 24,
  },
  rewardsCard: {
    backgroundColor: '#19376d',
    borderRadius: 12,
    padding: 20,
    marginBottom: 24,
  },
  rewardsTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
    textAlign: 'center',
  },
  rewardsList: {
    gap: 12,
  },
  rewardItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#0b2447',
    borderRadius: 8,
    padding: 12,
  },
  rewardIcon: {
    fontSize: 24,
    marginRight: 12,
  },
  rewardText: {
    fontSize: 16,
    color: '#fff',
    flex: 1,
  },
  actionsContainer: {
    gap: 12,
    marginBottom: 32,
  },
  actionButton: {
    padding: 16,
    borderRadius: 12,
    alignItems: 'center',
  },
  primaryButton: {
    backgroundColor: '#4a90e2',
  },
  secondaryButton: {
    backgroundColor: '#19376d',
    borderWidth: 2,
    borderColor: '#4a90e2',
  },
  tertiaryButton: {
    backgroundColor: 'transparent',
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  secondaryButtonText: {
    color: '#4a90e2',
    fontSize: 16,
    fontWeight: 'bold',
  },
  tertiaryButtonText: {
    color: '#a0c1d1',
    fontSize: 16,
  },
});

export default RunResults;

