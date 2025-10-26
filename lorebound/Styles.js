import { StyleSheet } from 'react-native';

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    padding: 20,
    backgroundColor: '#a5d7e8',
  },
  title: {
    fontSize: 48,
    fontWeight: '600',
    marginBottom: 40,
    textAlign: 'center',
    color: '#19376d'
  },
  lore:{
    color: '#ffffff',
  },
  bound:{
    color: '#19376d',
  },
  button: {
    backgroundColor: '#19376d',
    paddingVertical: 16,
    paddingHorizontal: 50,
    borderRadius: 20,
    marginBottom: 20,
  },
  smallButton: {
    backgroundColor: '#5260e0',
    paddingVertical: 12,
    paddingHorizontal: 40,
    borderRadius: 20,
    marginBottom: 40,
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "center",
    gap: 20,
  },
  dungeonButton: {
    backgroundColor: "#0C2454", 
    borderRadius: 20,
    width: 160,
    height: 80,
    justifyContent: "center",
    alignItems: "center",
    margin: 10,
    padding: 10,
  },
  dungeonTitle: {
  color: '#ffffff',
  fontSize: 22,
  fontFamily: 'serif',
  textAlign: 'center',
  textTransform: 'capitalize',
  },
  dungeonSelectText: {
    color: '#ffffff',
    fontSize: 22,
    fontFamily: 'serif',
    textTransform: 'capitalize',
  },
  buttonText: {
    color: '#ffffff',
    fontSize: 22,
    fontFamily: 'serif',
    textTransform: 'capitalize',
  },
  dungeonFloors: {
    color: "white",
    fontSize: 14,
    fontFamily: "serif",
    textAlign: "center",
  },
  headerBox: {
    backgroundColor: '#19376d',
    padding: 20,
    borderRadius: 4,
    marginBottom: 20,
  },
  headerText: {
    color: 'white',
    fontSize: 26,
    textAlign: 'center',
    fontFamily: 'serif',
  },
  headerSubText: {
    color: 'white',
    fontSize: 18,
    textAlign: 'center',
    marginTop: 5,
  },
  playButton: {
    backgroundColor: '#5260e0',
    marginTop: 10
  },
  playText: {
    color: 'white',
    fontSize: 20,
    fontFamily: 'serif',
  },

  headerBar: {
    paddingTop: 10,
    paddingHorizontal: 4,
    paddingBottom: 8,
    flexDirection: "row",
    alignItems: "center",
    justifyContent: "space-between",
    gap: 8,
  },
  backBtn: {
    paddingVertical: 10,
    paddingHorizontal: 14,
    borderRadius: 10,
  },
  backBtnText: { ...baseSerif(18), color: "#ffffff" },
  headerRightSpace: { width: 80, height: 1 },

  tableHeader: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 8,
    paddingVertical: 6,
  },
  th: { color: "#19376d", fontSize: 14, fontWeight: "700" },

  row: {
    flexDirection: "row",
    alignItems: "center",
    paddingHorizontal: 12,
    paddingVertical: 12,
    backgroundColor: "#0C2454", // matches your dungeonButton bg
    borderRadius: 20,
    marginHorizontal: 6,
  },
  separator: { height: 10 },

  rankText: {
    width: 36,
    color: "#ffffff",
    fontWeight: "900",
  },
  avatar: {
    width: 36,
    height: 36,
    borderRadius: 18,
    backgroundColor: "#5260e0",
    alignItems: "center",
    justifyContent: "center",
    marginRight: 12,
  },
  avatarText: { ...baseSerif(16), color: "#ffffff", fontWeight: "800" },
  rowCenter: { flex: 1 },
  nameText: { ...baseSerif(18), color: "#ffffff", fontWeight: "700" },
  metaText: { ...baseSerif(14), color: "#ffffff", opacity: 0.85, marginTop: 2 },
  scoreText: { width: 100, color: "#ffffff", fontWeight: "800", textAlign: "right" },
});

export default styles;