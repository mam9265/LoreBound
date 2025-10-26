import React, { useState, useCallback, useEffect } from "react";
import {View, Text, TouchableOpacity, FlatList, RefreshControl, StyleSheet, ActivityIndicator} from "react-native";
import styles from '../styles/Styles';
import LeaderboardService from '../services/LeaderboardService';

function Leaderboards({ navigation }) {
  const [data, setData] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedScope, setSelectedScope] = useState('alltime');
  const [totalParticipants, setTotalParticipants] = useState(0);
  const [periodKey, setPeriodKey] = useState('');

  const fetchLeaderboard = async (scope) => {
    try {
      setError(null);
      const leaderboardData = await LeaderboardService.getLeaderboard(scope, 100, 0);
      
      // Transform API data to match component format
      const transformedData = leaderboardData.entries.map(entry => ({
        id: entry.user_id,
        name: entry.handle,
        score: entry.score,
        runs: entry.total_runs,
        rank: entry.rank,
      }));
      
      setData(transformedData);
      setTotalParticipants(leaderboardData.total_participants);
      setPeriodKey(leaderboardData.period_key);
    } catch (error) {
      console.error('Failed to fetch leaderboard:', error);
      setError(error.message || 'Failed to load leaderboard');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLeaderboard(selectedScope);
  }, [selectedScope]);

  const onRefresh = () => {
    setRefreshing(true);
    fetchLeaderboard(selectedScope);
  };

  const handleScopeChange = (scope) => {
    if (scope !== selectedScope) {
      setSelectedScope(scope);
      setLoading(true);
    }
  };

  const renderRow = ({ item, index }) => {
    const rank = index + 1;
    return (
      <View style={sx.row}>
        <Text style={sx.rankText}>{rank}</Text>

        <View style={sx.avatar}>
          <Text style={sx.avatarText}>{item.name?.[0] ?? "?"}</Text>
        </View>

        <View style={sx.rowCenter}>
          <Text style={sx.nameText} numberOfLines={1}>
            {item.name}
          </Text>
          <Text style={sx.metaText}>{item.runs} runs</Text>
        </View>

        <Text style={sx.scoreText}>{item.score.toLocaleString()}</Text>
      </View>
    );
  };

  if (loading && !refreshing) {
    return (
      <View style={[styles.container, { justifyContent: "center", alignItems: "center" }]}>
        <ActivityIndicator size="large" color="#19376d" />
        <Text style={sx.loadingText}>Loading leaderboard...</Text>
      </View>
    );
  }

  return (
    <View style={[styles.container, { justifyContent: "flex-start" }]}>
      {/* header bar */}
      <View style={sx.headerBar}>
        <TouchableOpacity
          onPress={() => navigation?.goBack?.()}
          style={[styles.smallButton, sx.backBtn]}
        >
          <Text style={sx.backBtnText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>
          <Text style={styles.lore}>Lore</Text>
          <Text style={styles.bound}>Bound</Text>
        </Text>
        <View style={sx.headerRightSpace} />
      </View>

      {/* decorative header box */}
      <View style={styles.headerBox}>
        <Text style={styles.headerText}>Leaderboards</Text>
        <Text style={styles.headerSubText}>
          {LeaderboardService.getScopeDisplayName(selectedScope)} • {totalParticipants} Players
        </Text>
      </View>

      {/* Scope Switcher */}
      <View style={sx.scopeSwitcher}>
        <TouchableOpacity
          style={[sx.scopeTab, selectedScope === 'today' && sx.scopeTabActive]}
          onPress={() => handleScopeChange('today')}
        >
          <Text style={[sx.scopeTabText, selectedScope === 'today' && sx.scopeTabTextActive]}>
            Today
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[sx.scopeTab, selectedScope === 'weekly' && sx.scopeTabActive]}
          onPress={() => handleScopeChange('weekly')}
        >
          <Text style={[sx.scopeTabText, selectedScope === 'weekly' && sx.scopeTabTextActive]}>
            This Week
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[sx.scopeTab, selectedScope === 'alltime' && sx.scopeTabActive]}
          onPress={() => handleScopeChange('alltime')}
        >
          <Text style={[sx.scopeTabText, selectedScope === 'alltime' && sx.scopeTabTextActive]}>
            All-Time
          </Text>
        </TouchableOpacity>
      </View>

      {/* Error Message */}
      {error && (
        <View style={sx.errorContainer}>
          <Text style={sx.errorText}>{error}</Text>
          <TouchableOpacity onPress={() => fetchLeaderboard(selectedScope)} style={sx.retryButton}>
            <Text style={sx.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* table header */}
      <View style={sx.tableHeader}>
        <Text style={[sx.th, { width: 36 }]}>#</Text>
        <Text style={[sx.th, { flex: 1, marginLeft: 40 }]}>Player</Text>
        <Text style={[sx.th, { width: 100, textAlign: "right" }]}>Score</Text>
      </View>

      {/* list */}
      <FlatList
        data={data}
        keyExtractor={(item, index) => `${item.id}-${index}`}
        renderItem={renderRow}
        contentContainerStyle={{ paddingBottom: 24 }}
        ItemSeparatorComponent={() => <View style={sx.separator} />}
        ListEmptyComponent={() => (
          <View style={sx.emptyContainer}>
            <Text style={sx.emptyText}>No rankings yet for this period</Text>
            <Text style={sx.emptySubText}>Be the first to complete a run!</Text>
          </View>
        )}
        refreshControl={
          <RefreshControl
            refreshing={refreshing}
            onRefresh={onRefresh}
            tintColor="#19376d"
          />
        }
      />
    </View>
  );
}

export default Leaderboards;

const sx = StyleSheet.create({
  headerBar: {
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    paddingHorizontal: 16,
    paddingTop: 12,
    marginBottom: 8,
  },
  backBtn: {
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
    backgroundColor: "#19376d",
  },
  backBtnText: {
    color: "#fff",
    fontWeight: "600",
  },
  headerRightSpace: {
    width: 60, // balances layout since Back button is on the left
  },
  scopeSwitcher: {
    flexDirection: "row",
    paddingHorizontal: 16,
    marginBottom: 12,
    gap: 8,
  },
  scopeTab: {
    flex: 1,
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    backgroundColor: "#f0f0f0",
    alignItems: "center",
  },
  scopeTabActive: {
    backgroundColor: "#19376d",
  },
  scopeTabText: {
    fontSize: 14,
    fontWeight: "600",
    color: "#666",
  },
  scopeTabTextActive: {
    color: "#fff",
  },
  tableHeader: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderColor: "#ccc",
  },
  th: {
    fontSize: 14,
    fontWeight: "600",
    color: "#19376d",
  },
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  separator: {
    height: 1,
    backgroundColor: "#eee",
    marginHorizontal: 16,
  },
  rankText: {
    width: 24,
    fontWeight: "600",
    fontSize: 15,
    color: "#19376d",
  },
  avatar: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: "#19376d20",
    justifyContent: "center",
    alignItems: "center",
    marginLeft: 8,
  },
  avatarText: {
    color: "#19376d",
    fontWeight: "700",
  },
  rowCenter: {
    flex: 1,
    marginLeft: 12,
  },
  nameText: {
    fontSize: 15,
    fontWeight: "500",
    color: "#222",
  },
  metaText: {
    fontSize: 12,
    color: "#555",
  },
  scoreText: {
    width: 100,
    textAlign: "right",
    fontWeight: "700",
    color: "#19376d",
    fontSize: 15,
  },
  loadingText: {
    marginTop: 12,
    fontSize: 16,
    color: "#666",
  },
  errorContainer: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#ffebee",
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 8,
  },
  errorText: {
    color: "#c62828",
    fontSize: 14,
    fontWeight: "500",
    marginBottom: 8,
  },
  retryButton: {
    alignSelf: "flex-start",
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: "#c62828",
    borderRadius: 6,
  },
  retryButtonText: {
    color: "#fff",
    fontSize: 12,
    fontWeight: "600",
  },
  emptyContainer: {
    padding: 40,
    alignItems: "center",
  },
  emptyText: {
    fontSize: 16,
    fontWeight: "600",
    color: "#666",
    marginBottom: 8,
  },
  emptySubText: {
    fontSize: 14,
    color: "#999",
  },
});