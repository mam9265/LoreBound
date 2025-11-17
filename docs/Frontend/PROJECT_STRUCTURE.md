# LoreBound Frontend - Project Structure

## 📁 Directory Organization

The project follows a clean, professional React Native architecture:

```
lorebound/
├── src/                          # Source code directory
│   ├── screens/                  # Screen components
│   │   ├── AuthScreen.js         # Login/Registration screen
│   │   ├── MainMenu.js           # Main menu screen
│   │   ├── DailyChallenge.js     # Daily challenge screen
│   │   ├── DungeonSelect.js      # Dungeon selection screen
│   │   └── index.js              # Screen exports
│   │
│   ├── services/                 # Business logic & API services
│   │   ├── api.js                # API service layer
│   │   ├── authUtils.js          # Authentication utilities
│   │   └── index.js              # Service exports
│   │
│   ├── config/                   # Configuration files
│   │   ├── config.js             # API & app configuration
│   │   └── index.js              # Config exports
│   │
│   ├── styles/                   # Styling
│   │   ├── Styles.js             # Global styles
│   │   └── index.js              # Style exports
│   │
│   └── index.js                  # Main src exports
│
├── docs/                         # Project documentation
│   ├── AUTH_USAGE_EXAMPLES.md    # Authentication usage guide
│   ├── CONNECTION_SUMMARY.md     # Backend connection summary
│   ├── SETUP_BACKEND_CONNECTION.md  # Setup instructions
│   └── GRADLE_FIX.md             # Android Gradle fixes
│
├── android/                      # Android native code
├── ios/                          # iOS native code
├── __tests__/                    # Test files
│
├── App.js                        # Main app component
├── index.js                      # App entry point
├── package.json                  # Dependencies
├── babel.config.js               # Babel configuration
├── metro.config.js               # Metro bundler config
├── jest.config.js                # Jest test config
└── README.md                     # Project README
```

## 📂 Directory Details

### `/src/screens/`
Screen components that represent full app pages.

**Files:**
- `AuthScreen.js` - User authentication (login/register)
- `MainMenu.js` - Main navigation menu
- `DailyChallenge.js` - Daily trivia challenge
- `DungeonSelect.js` - Dungeon selection interface

**Usage:**
```javascript
import { AuthScreen, MainMenu } from './src/screens';
```

### `/src/services/`
Business logic, API calls, and utilities.

**Files:**
- `api.js` - HTTP client and API endpoints
- `authUtils.js` - Authentication helpers and token management

**Usage:**
```javascript
import { ApiService, AuthUtils } from './src/services';
```

### `/src/config/`
Configuration settings and constants.

**Files:**
- `config.js` - API URLs, timeouts, environment settings

**Usage:**
```javascript
import { API_BASE_URL, API_TIMEOUT } from './src/config';
```

### `/src/styles/`
Styling and theming.

**Files:**
- `Styles.js` - Global StyleSheet definitions

**Usage:**
```javascript
import styles from './src/styles';
```

### `/docs/`
Project documentation and guides.

**Files:**
- Authentication guides
- Setup instructions
- Backend connection docs
- Troubleshooting guides

## 🎯 Import Conventions

### Option 1: Direct Imports (Current)
```javascript
import AuthScreen from './src/screens/AuthScreen';
import ApiService from './src/services/api';
import styles from './src/styles/Styles';
```

### Option 2: Index Imports (Recommended)
```javascript
import { AuthScreen, MainMenu } from './src/screens';
import { ApiService, AuthUtils } from './src/services';
import { API_BASE_URL } from './src/config';
import styles from './src/styles';
```

## 📝 File Naming Conventions

- **Components:** PascalCase (e.g., `AuthScreen.js`)
- **Services:** camelCase (e.g., `authUtils.js`)
- **Config:** camelCase (e.g., `config.js`)
- **Styles:** PascalCase (e.g., `Styles.js`)
- **Index files:** lowercase `index.js`

## 🔄 Adding New Files

### Adding a New Screen
1. Create file in `src/screens/NewScreen.js`
2. Export in `src/screens/index.js`
3. Add navigation route in `App.js`

Example:
```javascript
// src/screens/ProfileScreen.js
import React from 'react';
import { View, Text } from 'react-native';
import styles from '../styles/Styles';

function ProfileScreen({ navigation }) {
  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profile</Text>
    </View>
  );
}

export default ProfileScreen;

// src/screens/index.js
export { default as ProfileScreen } from './ProfileScreen';

// App.js
import { ProfileScreen } from './src/screens';
<Stack.Screen name="Profile" component={ProfileScreen} />
```

### Adding a New Service
1. Create file in `src/services/newService.js`
2. Export in `src/services/index.js`
3. Import where needed

Example:
```javascript
// src/services/gameService.js
import ApiService from './api';
import { API_BASE_URL } from '../config';

class GameService {
  async startGame(dungeonId) {
    // Implementation
  }
}

export default new GameService();

// src/services/index.js
export { default as GameService } from './gameService';
```

### Adding New Styles
Add to `src/styles/Styles.js` or create modular style files:

```javascript
// For component-specific styles
// src/styles/AuthStyles.js
import { StyleSheet } from 'react-native';

export default StyleSheet.create({
  loginButton: {
    backgroundColor: '#19376d',
    padding: 15,
  },
});

// Import in component
import authStyles from '../styles/AuthStyles';
```

## 🧪 Testing Structure

Tests should mirror the source structure:

```
__tests__/
├── screens/
│   ├── AuthScreen.test.js
│   └── MainMenu.test.js
├── services/
│   ├── api.test.js
│   └── authUtils.test.js
└── integration/
    └── auth-flow.test.js
```

## 📦 Module Organization Benefits

### ✅ Advantages of This Structure:

1. **Separation of Concerns**
   - UI components separate from business logic
   - Configuration isolated from implementation
   - Easy to locate and modify code

2. **Scalability**
   - Add new features without cluttering root
   - Clear boundaries between modules
   - Easy to refactor or extract modules

3. **Maintainability**
   - Predictable file locations
   - Consistent import paths
   - Easy onboarding for new developers

4. **Testability**
   - Services can be tested independently
   - Mock imports easily
   - Clear dependencies

5. **Reusability**
   - Services can be shared across screens
   - Styles can be composed
   - Utilities are centralized

## 🔧 Configuration Management

### Environment-Specific Config

```javascript
// src/config/config.js
const configs = {
  development: {
    API_BASE_URL: 'http://localhost:8000',
    DEBUG: true,
  },
  production: {
    API_BASE_URL: 'https://api.lorebound.com',
    DEBUG: false,
  },
};

const config = __DEV__ ? configs.development : configs.production;
export default config;
```

## 📱 Screen Navigation Flow

```
AuthScreen
    ↓
MainMenu
    ├→ DungeonSelect
    ├→ DailyChallenge
    └→ Profile (future)
```

## 🎨 Styling Guidelines

### Global Styles (`src/styles/Styles.js`)
- App-wide colors and themes
- Common components (buttons, inputs)
- Layout patterns

### Component-Specific Styles
- Create separate style files for complex components
- Keep styles close to components if very specific
- Use StyleSheet.create() for performance

## 🚀 Performance Tips

1. **Lazy Loading**
   ```javascript
   const ProfileScreen = React.lazy(() => import('./src/screens/ProfileScreen'));
   ```

2. **Memoization**
   ```javascript
   const MemoizedComponent = React.memo(ExpensiveComponent);
   ```

3. **Code Splitting**
   - Separate large modules
   - Lazy load non-critical features
   - Use dynamic imports

## 📚 Further Reading

- [React Native Best Practices](https://reactnative.dev/docs/performance)
- [Project Documentation](./docs/)
- [API Documentation](./docs/SETUP_BACKEND_CONNECTION.md)

## 🔄 Migration Guide (Old → New)

If you have old imports, update them:

```javascript
// Old
import AuthScreen from './AuthScreen';
import styles from './Styles';
import ApiService from './api';

// New
import AuthScreen from './src/screens/AuthScreen';
import styles from './src/styles/Styles';
import ApiService from './src/services/api';

// Or use index imports
import { AuthScreen } from './src/screens';
import { ApiService } from './src/services';
import styles from './src/styles';
```

## ✨ Next Steps

1. ✅ Structure organized
2. ✅ Documentation complete
3. 🔄 Optional: Add more services (game, leaderboard, profile)
4. 🔄 Optional: Add component library
5. 🔄 Optional: Add theme system
6. 🔄 Optional: Add i18n for multi-language support

---

**Last Updated:** October 19, 2025
**Version:** 1.0.0

