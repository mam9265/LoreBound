import React from 'react';
import {
  View,
  Text,
  TouchableOpacity,
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
    isVictory = true,
    totalQuestions = 10,
    isDailyChallenge = false,
    challengeModifiers = {},
  } = route.params || {};

  const effectiveScore = score ?? runData?.total_score ?? 0;

  const accuracy = questionsAnswered > 0
    ? Math.round((correctAnswers / questionsAnswered) * 100)
    : 0;

  const rewards = runData?.summary?.rewards || [];
  const rewardCount = rewards.length;
  const firstTwoRewards = rewards.slice(0, 2).map(r => r.name).join(', ');
  const remainingRewards = rewardCount > 2 ? rewardCount - 2 : 0;

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
    navigation.navigate('RunHistory', { from: 'RunResults' });
  };

  const getShortMessage = () => {
    if (!isVictory) return 'Every run makes you stronger. Try again soon!';
    if (accuracy >= 90) return "Outstanding performance – you're a trivia master!";
    if (accuracy >= 75) return 'Great job – you really know your stuff!';
    if (accuracy >= 60) return 'Nice work – dungeon cleared!';
    return 'You made it through – aim for higher accuracy next time!';
  };

  return (
    <View style={resultStyles.container}>
      {/* TOP CONTENT */}
      <View style={resultStyles.topSection}>
        {/* Header */}
        <View style={resultStyles.header}>
          {isDailyChallenge && (
            <Text style={resultStyles.dailyBadge}>🏆 DAILY CHALLENGE 🏆</Text>
          )}

          <Text
            style={[
              resultStyles.title,
              !isVictory && resultStyles.defeatTitle,
            ]}
          >
            {isVictory ? 'Victory!' : 'Defeated!'}
          </Text>

          {!!dungeonName && (
            <Text style={resultStyles.subtitle}>{dungeonName}</Text>
          )}

          {isVictory ? (
            <Text style={resultStyles.victorySubtext}>
              {isDailyChallenge ? 'Challenge Complete!' : 'Dungeon Cleared!'}{' '}
              {questionsAnswered}/{totalQuestions} Questions
            </Text>
          ) : (
            <Text style={resultStyles.defeatSubtext}>
              You ran out of lives. {questionsAnswered}/{totalQuestions} Questions
            </Text>
          )}

          {isDailyChallenge && challengeModifiers.points_multiplier && (
            <Text style={resultStyles.bonusText}>
              ✨ {challengeModifiers.points_multiplier}x Points Bonus ✨
            </Text>
          )}

          {/* One-line performance message */}
          <Text style={resultStyles.messageText}>{getShortMessage()}</Text>
        </View>

        {/* Score + Stats row */}
        <View style={resultStyles.mainRow}>
          {/* Score Card */}
          <View style={resultStyles.scoreCard}>
            <Text style={resultStyles.scoreLabel}>Final Score</Text>
            <Text style={resultStyles.scoreValue}>{effectiveScore}</Text>
            {runData?.rank && (
              <Text style={resultStyles.rankText}>Rank: #{runData.rank}</Text>
            )}
          </View>

          {/* Stats Column */}
          <View style={resultStyles.statsColumn}>
            <View style={resultStyles.statRow}>
              <View style={resultStyles.statBox}>
                <Text style={resultStyles.statValue}>{questionsAnswered}</Text>
                <Text style={resultStyles.statLabel}>Questions</Text>
              </View>
              <View style={resultStyles.statBox}>
                <Text style={resultStyles.statValue}>{correctAnswers}</Text>
                <Text style={resultStyles.statLabel}>Correct</Text>
              </View>
            </View>

            <View style={resultStyles.statRow}>
              <View style={resultStyles.statBox}>
                <Text
                  style={[resultStyles.statValue, resultStyles.accuracyValue]}
                >
                  {accuracy}%
                </Text>
                <Text style={resultStyles.statLabel}>Accuracy</Text>
              </View>
              <View style={resultStyles.statBox}>
                <Text style={resultStyles.statValue}>{maxStreak}🔥</Text>
                <Text style={resultStyles.statLabel}>Best Streak</Text>
              </View>
            </View>
          </View>
        </View>

        {/* Compact Rewards Strip */}
        <View style={resultStyles.compactRewardsCard}>
          <Text style={resultStyles.compactRewardsTitle}>Rewards</Text>

          <View style={resultStyles.compactRewardsRow}>
            <Text style={resultStyles.rewardIcon}>⭐</Text>
            <Text style={resultStyles.compactRewardsText}>
              {Math.floor(effectiveScore / 10)} XP
            </Text>
          </View>

          {maxStreak >= 5 && (
            <View style={resultStyles.compactRewardsRow}>
              <Text style={resultStyles.rewardIcon}>🔥</Text>
              <Text style={resultStyles.compactRewardsText}>
                Streak Master Badge
              </Text>
            </View>
          )}

          {accuracy === 100 && (
            <View style={resultStyles.compactRewardsRow}>
              <Text style={resultStyles.rewardIcon}>💯</Text>
              <Text style={resultStyles.compactRewardsText}>Perfect Score!</Text>
            </View>
          )}

          {rewardCount > 0 && (
            <View style={resultStyles.compactRewardsRow}>
              <Text style={resultStyles.rewardIcon}>🎁</Text>
              <Text
                style={resultStyles.compactRewardsText}
                numberOfLines={1}
                ellipsizeMode="tail"
              >
                Items: {firstTwoRewards}
                {remainingRewards > 0 && ` + ${remainingRewards} more`}
              </Text>
            </View>
          )}
        </View>
      </View>

      {/* ACTION BUTTONS (2×2 GRID) */}
      <View style={resultStyles.actionsContainer}>
        <TouchableOpacity
          style={[
            resultStyles.actionButton,
            resultStyles.primaryButton,
            resultStyles.halfWidthButton,
          ]}
          onPress={handlePlayAgain}
        >
          <Text style={resultStyles.primaryButtonText}>Play Again</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            resultStyles.actionButton,
            resultStyles.secondaryButton,
            resultStyles.halfWidthButton,
          ]}
          onPress={handleViewLeaderboard}
        >
          <Text style={resultStyles.secondaryButtonText}>Leaderboard</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            resultStyles.actionButton,
            resultStyles.secondaryButton,
            resultStyles.halfWidthButton,
          ]}
          onPress={handleViewHistory}
        >
          <Text style={resultStyles.secondaryButtonText}>Run History</Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[
            resultStyles.actionButton,
            resultStyles.tertiaryButton,
            resultStyles.halfWidthButton,
          ]}
          onPress={handleMainMenu}
        >
          <Text style={resultStyles.tertiaryButtonText}>Main Menu</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
}

const resultStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0b2447',
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
  },
  topSection: {
    flex: 1,
  },

  // Header
  header: {
    alignItems: 'center',
    marginBottom: 8,
  },
  title: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 2,
  },
  subtitle: {
    fontSize: 14,
    color: '#a0c1d1',
  },
  defeatTitle: {
    color: '#ff4444',
  },
  victorySubtext: {
    fontSize: 12,
    color: '#4caf50',
    marginTop: 4,
    fontWeight: '600',
    textAlign: 'center',
  },
  defeatSubtext: {
    fontSize: 12,
    color: '#ff8888',
    marginTop: 4,
    fontWeight: '600',
    textAlign: 'center',
  },
  dailyBadge: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#ffd700',
    marginBottom: 4,
    textAlign: 'center',
  },
  bonusText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#4caf50',
    marginTop: 4,
    textAlign: 'center',
  },
  messageText: {
    fontSize: 11,
    color: '#a0c1d1',
    marginTop: 4,
    textAlign: 'center',
  },

  // Score + Stats
  mainRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  scoreCard: {
    flex: 0.9,
    backgroundColor: '#19376d',
    borderRadius: 12,
    paddingVertical: 10,
    paddingHorizontal: 8,
    alignItems: 'center',
    borderWidth: 2,
    borderColor: '#4a90e2',
    marginRight: 6,
  },
  scoreLabel: {
    fontSize: 12,
    color: '#a0c1d1',
    marginBottom: 2,
  },
  scoreValue: {
    fontSize: 26,
    fontWeight: 'bold',
    color: '#4a90e2',
  },
  rankText: {
    fontSize: 12,
    color: '#ffd700',
    marginTop: 4,
    fontWeight: 'bold',
  },

  statsColumn: {
    flex: 1.1,
  },
  statRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  statBox: {
    flex: 1,
    backgroundColor: '#19376d',
    borderRadius: 10,
    paddingVertical: 6,
    paddingHorizontal: 4,
    alignItems: 'center',
    marginHorizontal: 2,
  },
  statValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 2,
  },
  accuracyValue: {
    color: '#4caf50',
  },
  statLabel: {
    fontSize: 10,
    color: '#a0c1d1',
  },

  // Compact Rewards
  compactRewardsCard: {
    backgroundColor: '#19376d',
    borderRadius: 10,
    paddingVertical: 8,
    paddingHorizontal: 10,
    marginTop: 4,
  },
  compactRewardsTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  compactRewardsRow: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 2,
  },
  rewardIcon: {
    fontSize: 16,
    marginRight: 6,
  },
  compactRewardsText: {
    fontSize: 11,
    color: '#fff',
    flex: 1,
  },

  // Buttons
  actionsContainer: {
    marginTop: 8,
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  actionButton: {
    paddingVertical: 10,
    borderRadius: 10,
    alignItems: 'center',
    marginBottom: 6,
  },
  halfWidthButton: {
    width: '48%',
  },
  primaryButton: {
    backgroundColor: '#4a90e2',
  },
  secondaryButton: {
    backgroundColor: '#19376d',
    borderWidth: 1,
    borderColor: '#4a90e2',
  },
  tertiaryButton: {
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: '#a0c1d1',
  },
  primaryButtonText: {
    color: '#fff',
    fontSize: 14,
    fontWeight: 'bold',
  },
  secondaryButtonText: {
    color: '#4a90e2',
    fontSize: 13,
    fontWeight: 'bold',
  },
  tertiaryButtonText: {
    color: '#a0c1d1',
    fontSize: 13,
    fontWeight: 'bold',
  },
});

export default RunResults;
