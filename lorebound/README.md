# LoreBound - React Native Frontend

A trivia RPG mobile game built with React Native, featuring dungeon exploration and daily challenges.

## 📱 About

LoreBound is a mobile trivia game where players explore themed dungeons, answer questions, and compete on leaderboards. The app features user authentication, multiple game modes, and integration with a FastAPI backend.

## 🏗️ Project Structure

```
lorebound/
├── src/                    # Source code
│   ├── screens/           # Screen components
│   ├── services/          # API & business logic
│   ├── config/            # Configuration
│   └── styles/            # Styling
├── docs/                  # Documentation
├── android/               # Android native code
├── ios/                   # iOS native code
└── __tests__/             # Tests
```

📖 **[View Detailed Structure](./PROJECT_STRUCTURE.md)**

## ✨ Features

- 🔐 **User Authentication** - Login and registration with JWT tokens
- 🏰 **Dungeon Select** - Multiple themed trivia dungeons
- 📅 **Daily Challenge** - New challenge every day
- 🎮 **Game Sessions** - Track progress and scores
- 🏆 **Leaderboards** - Compete with other players
- 📊 **User Profiles** - View stats and achievements

## 🚀 Quick Start

### Prerequisites

- Node.js >= 20
- React Native development environment set up
- Android Studio (for Android) or Xcode (for iOS)
- FastAPI backend running (see backend repo)

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Install iOS dependencies (Mac only):**
   ```bash
   cd ios
   bundle install
   bundle exec pod install
   cd ..
   ```

3. **Configure API endpoint:**
   
   The app automatically configures the correct API URL:
   - Android Emulator: `http://10.0.2.2:8000`
   - iOS Simulator: `http://localhost:8000`
   - Physical Device: Update `src/config/config.js` with your computer's IP

### Running the App

1. **Start Metro bundler:**
   ```bash
   npm start
   ```

2. **Run on Android:**
   ```bash
   npm run android
   ```

3. **Run on iOS:**
   ```bash
   npm run ios
   ```

## 🔌 Backend Connection

The app connects to a FastAPI backend for authentication and game data.

### Setup Instructions

1. Start the backend server:
   ```bash
   cd lorebound-backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. The frontend will automatically connect to:
   - **Development**: `http://localhost:8000` (iOS) or `http://10.0.2.2:8000` (Android)
   - **Production**: Configure in `src/config/config.js`

📖 **[Detailed Setup Guide](./docs/SETUP_BACKEND_CONNECTION.md)**

## 📚 Documentation

- **[Project Structure](./PROJECT_STRUCTURE.md)** - Detailed directory organization
- **[Backend Connection](./docs/SETUP_BACKEND_CONNECTION.md)** - API setup and configuration
- **[Authentication Usage](./docs/AUTH_USAGE_EXAMPLES.md)** - How to use auth in your code
- **[Connection Summary](./docs/CONNECTION_SUMMARY.md)** - Overview of frontend-backend integration
- **[Gradle Fix](./docs/GRADLE_FIX.md)** - Android Gradle configuration

## 🛠️ Development

### Project Structure

```
src/
├── screens/          # Screen components (AuthScreen, MainMenu, etc.)
├── services/         # API services and utilities
│   ├── api.js       # HTTP client and API calls
│   └── authUtils.js # Authentication helpers
├── config/          # App configuration
│   └── config.js    # API URLs and settings
└── styles/          # Global styles
    └── Styles.js    # StyleSheet definitions
```

### Adding a New Screen

1. Create file in `src/screens/NewScreen.js`
2. Add to `src/screens/index.js`
3. Register route in `App.js`

Example:
```javascript
// src/screens/LeaderboardScreen.js
import React from 'react';
import { View, Text } from 'react-native';
import styles from '../styles/Styles';

function LeaderboardScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Leaderboard</Text>
    </View>
  );
}

export default LeaderboardScreen;
```

### Making API Calls

```javascript
import { ApiService, AuthUtils } from './src/services';

// Authenticated request with automatic token refresh
const data = await AuthUtils.authenticatedRequest(async (token) => {
  const response = await fetch(`${API_BASE_URL}/v1/some-endpoint`, {
    headers: { 'Authorization': `Bearer ${token}` }
  });
  return await response.json();
});
```

## 🧪 Testing

```bash
# Run tests
npm test

# Run tests with coverage
npm test -- --coverage

# Run specific test
npm test AuthScreen
```

## 📦 Building for Production

### Android

```bash
cd android
./gradlew assembleRelease
```

APK will be at: `android/app/build/outputs/apk/release/app-release.apk`

### iOS

1. Open `ios/lorebound.xcworkspace` in Xcode
2. Select "Product" → "Archive"
3. Follow App Store submission process

## 🔧 Troubleshooting

### Common Issues

**"Network request failed"**
- Check backend is running
- Verify API URL in `src/config/config.js`
- Check device/emulator can reach the backend

**Android Gradle errors**
- See [Gradle Fix Guide](./docs/GRADLE_FIX.md)
- Clean build: `cd android && ./gradlew clean`

**Metro bundler issues**
- Clear cache: `npm start -- --reset-cache`
- Delete node_modules: `rm -rf node_modules && npm install`

**iOS build errors**
- Clean build folder: Cmd+Shift+K in Xcode
- Reinstall pods: `cd ios && pod install`

### Debug Menu

- **Android**: Shake device or Ctrl+M (Cmd+M on Mac)
- **iOS**: Shake device or Cmd+D

## 📝 Scripts

```bash
npm start          # Start Metro bundler
npm run android    # Run on Android
npm run ios        # Run on iOS
npm test          # Run tests
npm run lint      # Run linter
```

## 🔐 Environment Variables

For sensitive configuration, create `.env`:

```env
API_BASE_URL=https://api.lorebound.com
API_TIMEOUT=10000
```

## 🎨 Styling

Global styles are in `src/styles/Styles.js`. Uses React Native StyleSheet API.

```javascript
import styles from './src/styles/Styles';

<View style={styles.container}>
  <Text style={styles.title}>LoreBound</Text>
</View>
```

## 📱 Supported Platforms

- ✅ Android (API 24+)
- ✅ iOS (14.0+)

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Test thoroughly
4. Submit a pull request

## 📄 License

[Your License Here]

## 🔗 Links

- [React Native Docs](https://reactnative.dev/docs/getting-started)
- [Backend Repository](../lorebound-backend)
- [API Documentation](http://localhost:8000/docs)

## 💡 Tips

- Use React Native Debugger for better debugging
- Enable Fast Refresh for instant feedback
- Check logs: `npx react-native log-android` or `npx react-native log-ios`
- Use TypeScript for better type safety (optional migration)

---

**Version:** 0.1.0  
**React Native:** 0.81.4  
**Last Updated:** October 19, 2025
