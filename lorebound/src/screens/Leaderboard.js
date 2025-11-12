import React, { useState, useCallback, useEffect, useRef } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  StyleSheet,
  ActivityIndicator,
} from "react-native";
import styles from "../styles/Styles";
import LeaderboardService from "../services/LeaderboardService";

const COL = { rank: 32, avatar: 32, gap1: 8, gap2: 12, score: 100 };

function Leaderboards({ navigation }) {
  const [data, setData] = useState([]);
  const [refreshing, setRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedScope, setSelectedScope] = useState("alltime");
  const [totalParticipants, setTotalParticipants] = useState(0);
  const [periodKey, setPeriodKey] = useState("");

  // Prevent stale responses from overwriting newer state
  const reqIdRef = useRef(0);

  const transformEntries = (entries) =>
    entries.map((e) => ({
      id: String(e.user_id ?? e.handle ?? `${e.rank}-${e.handle ?? "anon"}`),
      name: e.handle ?? "Unknown",
      score: Number(e.score) || 0,
      runs: e.total_runs ?? 0,
      rank: e.rank ?? null,
    }));

  const fetchLeaderboard = useCallback(async (scope) => {
    const myReq = ++reqIdRef.current;
    try {
      setError(null);
      const res = await LeaderboardService.getLeaderboard(scope, 100, 0);
      if (myReq !== reqIdRef.current) return; // stale response guard

      setData(transformEntries(res.entries ?? []));
      setTotalParticipants(res.total_participants ?? 0);
      setPeriodKey(res.period_key ?? "");
    } catch (err) {
      if (myReq !== reqIdRef.current) return; // stale response guard
      console.error("Failed to fetch leaderboard:", err);
      setError(err?.message ?? "Failed to load leaderboard");
    } finally {
      if (myReq === reqIdRef.current) {
        setLoading(false);
        setRefreshing(false);
      }
    }
  }, []);

  useEffect(() => {
    setLoading(true);
    fetchLeaderboard(selectedScope);
    // Cancel in-flight responses on unmount or scope change
    return () => {
      reqIdRef.current++;
    };
  }, [selectedScope, fetchLeaderboard]);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    fetchLeaderboard(selectedScope);
  }, [fetchLeaderboard, selectedScope]);

  const retry = useCallback(() => {
    setLoading(true);
    fetchLeaderboard(selectedScope);
  }, [fetchLeaderboard, selectedScope]);

  const handleScopeChange = useCallback(
    (scope) => {
      if (scope !== selectedScope) {
        setSelectedScope(scope);
        setLoading(true);
      }
    },
    [selectedScope]
  );

  const renderRow = useCallback(({ item }) => {
    const rank = item.rank ?? "-";
    const initials = (item.name ?? "?")
      .trim()
      .split(/\s+/)
      .map((s) => s[0])
      .join("")
      .slice(0, 2)
      .toUpperCase();

    return (
      <View style={sx.row}>
        <Text style={[sx.rankText, { width: COL.rank }]}>{rank}</Text>

        <View style={[sx.avatar, { width: COL.avatar, height: COL.avatar, borderRadius: COL.avatar / 2, marginLeft: COL.gap1 }]}>
          <Text style={sx.avatarText}>{initials}</Text>
        </View>

        <View style={[sx.rowCenter, { marginLeft: COL.gap2 }]}>
          <Text style={sx.nameText} numberOfLines={1}>
            {item.name}
          </Text>
          <Text style={sx.metaText}>{item.runs} runs</Text>
        </View>

        <Text style={[sx.scoreText, { width: COL.score }]}>
          {Number.isFinite(item.score) ? item.score.toLocaleString() : "—"}
        </Text>
      </View>
    );
  }, []);

  const ItemSeparatorComponent = useCallback(() => <View style={sx.separator} />, []);

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
      {/* Header bar */}
      <View style={sx.headerBar}>
        <TouchableOpacity
          onPress={() => navigation?.goBack?.()}
          style={[styles.smallButton, sx.backBtn]}
          accessibilityRole="button"
          accessibilityLabel="Go back"
        >
          <Text style={sx.backBtnText}>← Back</Text>
        </TouchableOpacity>
        <Text style={styles.title}>
          <Text style={styles.lore}>Lore</Text>
          <Text style={styles.bound}>Bound</Text>
        </Text>
        <View style={sx.headerRightSpace} />
      </View>

      {/* Decorative header box */}
      <View style={styles.headerBox}>
        <Text style={styles.headerText}>Leaderboards</Text>
        <Text style={styles.headerSubText}>
          {LeaderboardService.getScopeDisplayName(selectedScope)}
          {periodKey ? ` • ${periodKey}` : ""} • {totalParticipants} Players
        </Text>
      </View>

      {/* Scope Switcher */}
      <View style={sx.scopeSwitcher}>
        <TouchableOpacity
          style={[sx.scopeTab, selectedScope === "today" && sx.scopeTabActive]}
          onPress={() => handleScopeChange("today")}
          accessibilityRole="button"
          accessibilityState={{ selected: selectedScope === "today" }}
        >
          <Text style={[sx.scopeTabText, selectedScope === "today" && sx.scopeTabTextActive]}>
            Today
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[sx.scopeTab, selectedScope === "weekly" && sx.scopeTabActive]}
          onPress={() => handleScopeChange("weekly")}
          accessibilityRole="button"
          accessibilityState={{ selected: selectedScope === "weekly" }}
        >
          <Text style={[sx.scopeTabText, selectedScope === "weekly" && sx.scopeTabTextActive]}>
            This Week
          </Text>
        </TouchableOpacity>
        <TouchableOpacity
          style={[sx.scopeTab, selectedScope === "alltime" && sx.scopeTabActive]}
          onPress={() => handleScopeChange("alltime")}
          accessibilityRole="button"
          accessibilityState={{ selected: selectedScope === "alltime" }}
        >
          <Text style={[sx.scopeTabText, selectedScope === "alltime" && sx.scopeTabTextActive]}>
            All-Time
          </Text>
        </TouchableOpacity>
      </View>

      {/* Error Message */}
      {error && (
        <View style={sx.errorContainer}>
          <Text style={sx.errorText}>{error}</Text>
          <TouchableOpacity onPress={retry} style={sx.retryButton}>
            <Text style={sx.retryButtonText}>Retry</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* Table header */}
      <View style={sx.tableHeader}>
        <Text style={[sx.th, { width: COL.rank }]}>#</Text>
        <Text style={[sx.th, { flex: 1, marginLeft: COL.avatar + COL.gap1 + COL.gap2 }]}>Player</Text>
        <Text style={[sx.th, { width: COL.score, textAlign: "right" }]}>Score</Text>
      </View>

      {/* List */}
      <FlatList
        data={data}
        keyExtractor={(item) => String(item.id)}
        renderItem={renderRow}
        contentContainerStyle={{ paddingBottom: 24 }}
        ItemSeparatorComponent={ItemSeparatorComponent}
        ListEmptyComponent={() => (
          <View style={sx.emptyContainer}>
            <Text style={sx.emptyText}>No rankings yet for this period</Text>
            <Text style={sx.emptySubText}>Be the first to complete a run!</Text>
          </View>
        )}
        refreshControl={<RefreshControl refreshing={refreshing} onRefresh={onRefresh} tintColor="#19376d" />}
        ListFooterComponent={<View style={{ height: 8 }} />}
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
  headerRightSpace: { width: 60 },
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
  scopeTabActive: { backgroundColor: "#19376d" },
  scopeTabText: { fontSize: 14, fontWeight: "600", color: "#666" },
  scopeTabTextActive: { color: "#fff" },
  tableHeader: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 8,
    borderBottomWidth: 1,
    borderColor: "#ccc",
  },
  th: { fontSize: 14, fontWeight: "600", color: "#19376d" },
  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 16,
    paddingVertical: 10,
  },
  separator: { height: 1, backgroundColor: "#eee", marginHorizontal: 16 },
  rankText: {
    fontWeight: "600",
    fontSize: 15,
    color: "#19376d",
  },
  avatar: {
    backgroundColor: "#19376d20",
    justifyContent: "center",
    alignItems: "center",
  },
  avatarText: { color: "#19376d", fontWeight: "700" },
  rowCenter: { flex: 1 },
  nameText: { fontSize: 15, fontWeight: "500", color: "#222" },
  metaText: { fontSize: 12, color: "#555" },
  scoreText: {
    textAlign: "right",
    fontWeight: "700",
    color: "#19376d",
    fontSize: 15,
  },
  loadingText: { marginTop: 12, fontSize: 16, color: "#666" },
  errorContainer: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    backgroundColor: "#ffebee",
    marginHorizontal: 16,
    marginBottom: 12,
    borderRadius: 8,
  },
  errorText: { color: "#c62828", fontSize: 14, fontWeight: "500", marginBottom: 8 },
  retryButton: {
    alignSelf: "flex-start",
    paddingHorizontal: 12,
    paddingVertical: 6,
    backgroundColor: "#c62828",
    borderRadius: 6,
  },
  retryButtonText: { color: "#fff", fontSize: 12, fontWeight: "600" },
  emptyContainer: { padding: 40, alignItems: "center" },
  emptyText: { fontSize: 16, fontWeight: "600", color: "#666", marginBottom: 8 },
  emptySubText: { fontSize: 14, color: "#999" },
});
