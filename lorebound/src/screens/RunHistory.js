import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  ActivityIndicator,
  RefreshControl,
  StyleSheet,
  Alert,
} from 'react-native';
import { RunService } from '../services';
import styles from '../styles/Styles';

function RunHistory({ navigation }) {
  const [runs, setRuns] = useState([]);
  const [stats, setStats] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [hasMore, setHasMore] = useState(true);
  const [offset, setOffset] = useState(0);
  const LIMIT = 20;

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setIsLoading(true);
      const [runsData, statsData] = await Promise.all([
        RunService.getUserRuns(LIMIT, 0),
        RunService.getUserStats(),
      ]);
      
      setRuns(runsData);
      setStats(statsData);
      setOffset(LIMIT);
      setHasMore(runsData.length === LIMIT);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to load run history:', error);
      Alert.alert('Error', 'Failed to load run history. Please try again.');
      setIsLoading(false);
    }
  };

  const handleRefresh = useCallback(async () => {
    try {
      setIsRefreshing(true);
      const [runsData, statsData] = await Promise.all([
        RunService.getUserRuns(LIMIT, 0),
        RunService.getUserStats(),
      ]);
      
      setRuns(runsData);
      setStats(statsData);
      setOffset(LIMIT);
      setHasMore(runsData.length === LIMIT);
      setIsRefreshing(false);
    } catch (error) {
      console.error('Failed to refresh run history:', error);
      setIsRefreshing(false);
    }
  }, []);

  const loadMore = async () => {
    if (!hasMore || isLoading || isRefreshing) return;

    try {
      const moreRuns = await RunService.getUserRuns(LIMIT, offset);
      setRuns([...runs, ...moreRuns]);
      setOffset(offset + LIMIT);
      setHasMore(moreRuns.length === LIMIT);
    } catch (error) {
      console.error('Failed to load more runs:', error);
    }
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'completed':
        return '#4caf50';
      case 'abandoned':
        return '#ff9800';
      case 'failed':
        return '#f44336';
      default:
        return '#a0c1d1';
    }
  };

  const getStatusEmoji = (status) => {
    switch (status) {
      case 'completed':
        return '✅';
      case 'abandoned':
        return '⏸️';
      case 'failed':
        return '❌';
      default:
        return '⏳';
    }
  };

  const renderRunItem = ({ item }) => (
    <TouchableOpacity
      style={historyStyles.runCard}
      onPress={() => {
        // Navigate to run details if needed
        Alert.alert('Run Details', `Run ID: ${item.id}\nStatus: ${item.status}`);
      }}
    >
      <View style={historyStyles.runHeader}>
        <View style={historyStyles.runTitleRow}>
          <Text style={historyStyles.runTitle}>
            {item.dungeon?.title || 'Unknown Dungeon'}
          </Text>
          <Text style={historyStyles.runEmoji}>{getStatusEmoji(item.status)}</Text>
        </View>
        <Text style={historyStyles.runDate}>{formatDate(item.started_at)}</Text>
      </View>

      <View style={historyStyles.runStats}>
        <View style={historyStyles.runStat}>
          <Text style={historyStyles.runStatLabel}>Score</Text>
          <Text style={historyStyles.runStatValue}>
            {item.total_score || 0}
          </Text>
        </View>

        <View style={historyStyles.runStat}>
          <Text style={historyStyles.runStatLabel}>Floor</Text>
          <Text style={historyStyles.runStatValue}>{item.floor || 1}</Text>
        </View>

        <View style={historyStyles.runStat}>
          <Text style={historyStyles.runStatLabel}>Status</Text>
          <Text
            style={[
              historyStyles.runStatValue,
              { color: getStatusColor(item.status) },
            ]}
          >
            {item.status}
          </Text>
        </View>
      </View>

      {item.completed_at && (
        <Text style={historyStyles.runDuration}>
          Duration: {Math.round(
            (new Date(item.completed_at) - new Date(item.started_at)) / 1000 / 60
          )}m
        </Text>
      )}
    </TouchableOpacity>
  );

  const renderHeader = () => (
    <View>
      {/* Stats Summary */}
      {stats && (
        <View style={historyStyles.statsContainer}>
          <Text style={historyStyles.statsTitle}>Your Stats</Text>
          
          <View style={historyStyles.statsGrid}>
            <View style={historyStyles.statsCard}>
              <Text style={historyStyles.statsValue}>{stats.total_runs}</Text>
              <Text style={historyStyles.statsLabel}>Total Runs</Text>
            </View>

            <View style={historyStyles.statsCard}>
              <Text style={historyStyles.statsValue}>
                {Math.round(stats.average_score)}
              </Text>
              <Text style={historyStyles.statsLabel}>Avg Score</Text>
            </View>

            <View style={historyStyles.statsCard}>
              <Text style={historyStyles.statsValue}>{stats.best_score}</Text>
              <Text style={historyStyles.statsLabel}>Best Score</Text>
            </View>

            <View style={historyStyles.statsCard}>
              <Text style={[historyStyles.statsValue, historyStyles.accuracyValue]}>
                {Math.round(stats.accuracy_percentage)}%
              </Text>
              <Text style={historyStyles.statsLabel}>Accuracy</Text>
            </View>
          </View>
        </View>
      )}

      {/* Run History Title */}
      <View style={historyStyles.sectionHeader}>
        <Text style={historyStyles.sectionTitle}>Run History</Text>
        <Text style={historyStyles.sectionSubtitle}>
          {runs.length} run{runs.length !== 1 ? 's' : ''}
        </Text>
      </View>
    </View>
  );

  const renderFooter = () => {
    if (!hasMore) return null;
    return (
      <View style={historyStyles.footer}>
        <ActivityIndicator size="small" color="#4a90e2" />
      </View>
    );
  };

  const renderEmpty = () => (
    <View style={historyStyles.emptyContainer}>
      <Text style={historyStyles.emptyIcon}>🎮</Text>
      <Text style={historyStyles.emptyTitle}>No Runs Yet</Text>
      <Text style={historyStyles.emptyText}>
        Start your first dungeon run to see your history here!
      </Text>
      <TouchableOpacity
        style={historyStyles.startButton}
        onPress={() => navigation.navigate('DungeonSelect')}
      >
        <Text style={historyStyles.startButtonText}>Start a Run</Text>
      </TouchableOpacity>
    </View>
  );

  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator size="large" color="#19376d" />
        <Text style={[styles.headerText, { marginTop: 20 }]}>
          Loading History...
        </Text>
      </View>
    );
  }

  return (
    <View style={historyStyles.container}>
      {/* Header Bar */}
      <View style={historyStyles.headerBar}>
        <TouchableOpacity
          onPress={() => navigation.goBack()}
          style={historyStyles.backButton}
        >
          <Text style={historyStyles.backButtonText}>← Back</Text>
        </TouchableOpacity>
        <Text style={historyStyles.headerTitle}>Run History</Text>
        <View style={historyStyles.placeholder} />
      </View>

      {/* List */}
      <FlatList
        data={runs}
        renderItem={renderRunItem}
        keyExtractor={(item) => item.id}
        ListHeaderComponent={renderHeader}
        ListFooterComponent={renderFooter}
        ListEmptyComponent={renderEmpty}
        refreshControl={
          <RefreshControl
            refreshing={isRefreshing}
            onRefresh={handleRefresh}
            tintColor="#4a90e2"
          />
        }
        onEndReached={loadMore}
        onEndReachedThreshold={0.5}
        contentContainerStyle={historyStyles.listContent}
      />
    </View>
  );
}

const historyStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0b2447',
  },
  headerBar: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 16,
    backgroundColor: '#19376d',
    borderBottomWidth: 2,
    borderBottomColor: '#0b2447',
  },
  backButton: {
    padding: 8,
  },
  backButtonText: {
    color: '#4a90e2',
    fontSize: 16,
    fontWeight: 'bold',
  },
  headerTitle: {
    color: '#fff',
    fontSize: 20,
    fontWeight: 'bold',
  },
  placeholder: {
    width: 60,
  },
  listContent: {
    padding: 16,
  },
  statsContainer: {
    marginBottom: 24,
  },
  statsTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 16,
  },
  statsGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
  },
  statsCard: {
    width: '48%',
    backgroundColor: '#19376d',
    borderRadius: 12,
    padding: 16,
    alignItems: 'center',
    marginBottom: 12,
  },
  statsValue: {
    fontSize: 28,
    fontWeight: 'bold',
    color: '#4a90e2',
    marginBottom: 4,
  },
  accuracyValue: {
    color: '#4caf50',
  },
  statsLabel: {
    fontSize: 14,
    color: '#a0c1d1',
  },
  sectionHeader: {
    marginBottom: 16,
  },
  sectionTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 4,
  },
  sectionSubtitle: {
    fontSize: 14,
    color: '#a0c1d1',
  },
  runCard: {
    backgroundColor: '#19376d',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#2c5f8d',
  },
  runHeader: {
    marginBottom: 12,
  },
  runTitleRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 4,
  },
  runTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#fff',
    flex: 1,
  },
  runEmoji: {
    fontSize: 20,
  },
  runDate: {
    fontSize: 14,
    color: '#a0c1d1',
  },
  runStats: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingTop: 12,
    borderTopWidth: 1,
    borderTopColor: '#2c5f8d',
  },
  runStat: {
    alignItems: 'center',
  },
  runStatLabel: {
    fontSize: 12,
    color: '#a0c1d1',
    marginBottom: 4,
  },
  runStatValue: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#fff',
  },
  runDuration: {
    fontSize: 12,
    color: '#a0c1d1',
    marginTop: 8,
    textAlign: 'right',
  },
  footer: {
    padding: 20,
    alignItems: 'center',
  },
  emptyContainer: {
    alignItems: 'center',
    paddingVertical: 60,
    paddingHorizontal: 40,
  },
  emptyIcon: {
    fontSize: 64,
    marginBottom: 16,
  },
  emptyTitle: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#fff',
    marginBottom: 12,
  },
  emptyText: {
    fontSize: 16,
    color: '#a0c1d1',
    textAlign: 'center',
    lineHeight: 24,
    marginBottom: 24,
  },
  startButton: {
    backgroundColor: '#4a90e2',
    paddingVertical: 12,
    paddingHorizontal: 32,
    borderRadius: 8,
  },
  startButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
});

export default RunHistory;

