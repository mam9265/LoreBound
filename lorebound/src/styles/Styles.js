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
  scrollContainer: {
    flexGrow: 1,
    backgroundColor: '#a5d7e8',
    alignItems: 'center',
    paddingVertical: 20,
  },
  // Auth Screen Styles
  authContainer: {
    flex: 1,
    backgroundColor: '#a5d7e8',
  },

  authInnerContainer: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    paddingHorizontal: 20,
  },

  authFormContainer: {
    width: '100%',
    maxWidth: 400,
    backgroundColor: '#fff',
    borderRadius: 15,
    padding: 20,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.1,
    shadowRadius: 5,
    elevation: 3,
  },

  inputContainer: {
    marginBottom: 15,
  },

  input: {
    borderWidth: 1,
    borderColor: '#19376d',
    borderRadius: 8,
    padding: 10,
    fontSize: 16,
  },

  authScrollContent: {
    flexGrow: 1,
    justifyContent: 'center',
    padding: 20,
  },
  authTitleContainer: {
    marginBottom: 40,
    alignItems: 'center',
  },
  authTitle: {
    fontSize: 56,
    fontWeight: '700',
    marginBottom: 10,
    textAlign: 'center',
  },
  authSubtitle: {
    fontSize: 20,
    color: '#19376d',
    textAlign: 'center',
    fontFamily: 'serif',
    marginTop: 10,
  },
  inputLabel: {
    fontSize: 16,
    color: '#19376d',
    marginBottom: 8,
    fontWeight: '600',
    fontFamily: 'serif',
  },
  authButton: {
    backgroundColor: '#19376d',
    paddingVertical: 16,
    borderRadius: 12,
    marginTop: 10,
    shadowColor: '#000',
    shadowOffset: {
      width: 0,
      height: 2,
    },
    shadowOpacity: 0.25,
    shadowRadius: 3.84,
    elevation: 5,
  },
  authButtonDisabled: {
    backgroundColor: '#7a8fa8',
    opacity: 0.7,
  },
  authButtonText: {
    color: '#ffffff',
    fontSize: 20,
    fontWeight: '700',
    textAlign: 'center',
    fontFamily: 'serif',
    textTransform: 'uppercase',
  },
  authToggleContainer: {
    flexDirection: 'row',
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 24,
  },
  authToggleText: {
    fontSize: 15,
    color: '#666',
  },
  authToggleLink: {
    fontSize: 15,
    color: '#5260e0',
    fontWeight: '700',
    textDecorationLine: 'underline',
  },
  header: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
    marginBottom: 20,
    textAlign: 'center',
  },
  previewContainer: {
    alignItems: 'center',
    marginBottom: 20,
  },
  characterContainer: {
    width: '95%',
    backgroundColor: '#a5d7e8',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
  },
  characterImage: {
    width: 200,
    height: 200,
    marginBottom: 10,
  },
  previewText: {
    color: '#aaa',
    fontSize: 16,
    marginBottom: 5,
  },
  equipmentText: {
    color: '#fff',
    fontSize: 16,
  },
  buttonWrapper: {
    width: '100%',
    marginVertical: 10,
  },
  optionGroup: {
    width: '100%',
    marginVertical: 10,
    padding: 10,
    backgroundColor: '#eaf6ff',
    borderRadius: 10,
  },
  optionLabel: {
    fontSize: 16,
    fontWeight: '500',
    marginBottom: 5,
    color: '#19376d',
  },
  saveButton: {
    marginTop: 30,
    backgroundColor: '#4e9bde',
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  saveText: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
});

export default styles;