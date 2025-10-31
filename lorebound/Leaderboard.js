import React, { useMemo, useState, useCallback } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  RefreshControl,
  StyleSheet,
} from "react-native";
import styles from "./Styles"; // your stylesheet

function Leaderboards({ navigation }) {
  // mock data (sorted by score desc)
  const data = useMemo(
    () =>
      [
        { id: "1", name: "Astra", score: 9876, runs: 142 },
        { id: "2", name: "Kane", score: 9530, runs: 120 },
        { id: "3", name: "Lyra", score: 9205, runs: 110 },
        { id: "4", name: "Cipher", score: 8990, runs: 101 },
        { id: "5", name: "Nova", score: 8750, runs: 99 },
        { id: "6", name: "Rook", score: 8602, runs: 95 },
        { id: "7", name: "Echo", score: 8450, runs: 90 },
        { id: "8", name: "Vex", score: 8321, runs: 88 },
        { id: "9", name: "Jade", score: 8204, runs: 84 },
        { id: "10", name: "Grit", score: 8100, runs: 82 },
        { id: "11", name: "Zuri", score: 7999, runs: 81 },
        { id: "12", name: "Bolt", score: 7895, runs: 79 },
        { id: "13", name: "Mira", score: 7704, runs: 76 },
        { id: "14", name: "Onyx", score: 7620, runs: 74 },
        { id: "15", name: "Slate", score: 7555, runs: 72 },
      ].sort((a, b) => b.score - a.score),
    []
  );

  const [refreshing, setRefreshing] = useState(false);

  const onRefresh = useCallback(() => {
    setRefreshing(true);
    // simulate fetch
    setTimeout(() => setRefreshing(false), 800);
  }, []);

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
        <Text style={styles.headerSubText}>All-Time • Highest Scores</Text>
      </View>

      {/* table header */}
      <View style={sx.tableHeader}>
        <Text style={[sx.th, { width: 36 }]}>#</Text>
        <Text style={[sx.th, { flex: 1, marginLeft: 40 }]}>Player</Text>
        <Text style={[sx.th, { width: 100, textAlign: "right" }]}>Score</Text>
      </View>

      {/* list */}
      <FlatList
        data={data}
        keyExtractor={(item) => item.id}
        renderItem={renderRow}
        contentContainerStyle={{ paddingBottom: 24 }}
        ItemSeparatorComponent={() => <View style={sx.separator} />}
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

