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
});

export default styles;