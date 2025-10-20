# Authentication Usage Examples

This guide shows how to use the authentication system in other screens and components.

## 🔐 Basic Authentication Check

### Check if User is Logged In

```javascript
import AuthUtils from './authUtils';

// In any component
const checkAuth = async () => {
  const isAuthenticated = await AuthUtils.isAuthenticated();
  
  if (!isAuthenticated) {
    // Redirect to login
    navigation.navigate('AuthScreen');
  }
};
```

### Get Current User Data

```javascript
import AuthUtils from './authUtils';

// Get cached user data (fast, no network call)
const userData = await AuthUtils.getUserData();
console.log('User:', userData.email);

// Get fresh user data from backend (with auto token refresh)
const freshUserData = await AuthUtils.getCurrentUserProfile();
console.log('User:', freshUserData.email);
```

## 📱 Example: MainMenu with Logout

```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Alert } from 'react-native';
import AuthUtils from './authUtils';
import styles from './Styles';

function MainMenu({ navigation }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadUserData();
  }, []);

  const loadUserData = async () => {
    try {
      const userData = await AuthUtils.getUserData();
      if (userData) {
        setUser(userData);
      } else {
        // No user data, redirect to login
        navigation.replace('AuthScreen');
      }
    } catch (error) {
      console.error('Error loading user:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    Alert.alert(
      'Logout',
      'Are you sure you want to logout?',
      [
        {
          text: 'Cancel',
          style: 'cancel',
        },
        {
          text: 'Logout',
          style: 'destructive',
          onPress: async () => {
            try {
              await AuthUtils.logout();
              navigation.replace('AuthScreen');
            } catch (error) {
              Alert.alert('Error', 'Failed to logout');
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <Text>Loading...</Text>
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Main Menu</Text>
      {user && (
        <Text style={styles.headerSubText}>
          Welcome, {user.email}!
        </Text>
      )}
      
      {/* Your existing menu buttons */}
      
      <TouchableOpacity 
        style={styles.button}
        onPress={handleLogout}
      >
        <Text style={styles.buttonText}>Logout</Text>
      </TouchableOpacity>
    </View>
  );
}

export default MainMenu;
```

## 🔒 Example: Protected API Request

### Making an Authenticated Request

```javascript
import ApiService from './api';
import AuthUtils from './authUtils';

// Option 1: Manual token management
const fetchProtectedData = async () => {
  try {
    const token = await AuthUtils.getAccessToken();
    
    const response = await fetch('http://localhost:8000/v1/some-endpoint', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
    });
    
    if (!response.ok) {
      throw new Error('Request failed');
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};

// Option 2: Using authenticatedRequest helper (with auto token refresh)
const fetchProtectedDataWithAutoRefresh = async () => {
  try {
    const data = await AuthUtils.authenticatedRequest(async (token) => {
      const response = await fetch('http://localhost:8000/v1/some-endpoint', {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        throw new Error('Request failed');
      }
      
      return await response.json();
    });
    
    return data;
  } catch (error) {
    console.error('Error:', error);
    throw error;
  }
};
```

## 🎮 Example: DailyChallenge Screen with Auth

```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import AuthUtils from './authUtils';
import { API_BASE_URL } from './config';
import styles from './Styles';

function DailyChallenge({ navigation }) {
  const [challenge, setChallenge] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDailyChallenge();
  }, []);

  const loadDailyChallenge = async () => {
    try {
      // Check authentication first
      const isAuth = await AuthUtils.isAuthenticated();
      if (!isAuth) {
        navigation.replace('AuthScreen');
        return;
      }

      // Fetch daily challenge with auto token refresh
      const data = await AuthUtils.authenticatedRequest(async (token) => {
        const response = await fetch(`${API_BASE_URL}/v1/content/daily`, {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
        
        if (!response.ok) {
          throw new Error('Failed to fetch daily challenge');
        }
        
        return await response.json();
      });
      
      setChallenge(data);
    } catch (error) {
      console.error('Error loading challenge:', error);
      Alert.alert('Error', 'Failed to load daily challenge');
    } finally {
      setLoading(false);
    }
  };

  const handlePlay = async () => {
    // Start game run with authentication
    try {
      const runData = await AuthUtils.authenticatedRequest(async (token) => {
        const response = await fetch(`${API_BASE_URL}/v1/runs/start`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            dungeon_id: challenge.dungeon_id,
            difficulty: 'normal',
          }),
        });
        
        if (!response.ok) {
          throw new Error('Failed to start game');
        }
        
        return await response.json();
      });
      
      // Navigate to game screen with run data
      navigation.navigate('GameScreen', { run: runData });
    } catch (error) {
      console.error('Error starting game:', error);
      Alert.alert('Error', 'Failed to start game');
    }
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#19376d" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Daily Challenge</Text>
      {challenge && (
        <>
          <Text style={styles.headerText}>{challenge.name}</Text>
          <Text style={styles.headerSubText}>{challenge.description}</Text>
          <TouchableOpacity 
            style={styles.button}
            onPress={handlePlay}
          >
            <Text style={styles.buttonText}>Play</Text>
          </TouchableOpacity>
        </>
      )}
    </View>
  );
}

export default DailyChallenge;
```

## 🔄 Example: Auto-Login on App Start

### Update App.js to check for existing session

```javascript
import React, { useState, useEffect } from 'react';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { View, ActivityIndicator } from 'react-native';
import AuthUtils from './authUtils';

import AuthScreen from './AuthScreen';
import MainMenu from './MainMenu';
import DungeonSelect from './DungeonSelect';
import DailyChallenge from './DailyChallenge';

const Stack = createNativeStackNavigator();

export default function App() {
  const [initialRoute, setInitialRoute] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthentication();
  }, []);

  const checkAuthentication = async () => {
    try {
      const isAuth = await AuthUtils.isAuthenticated();
      
      if (isAuth) {
        // Try to get fresh user profile to validate token
        const profile = await AuthUtils.getCurrentUserProfile();
        
        if (profile) {
          // Valid token, go to MainMenu
          setInitialRoute('MainMenu');
        } else {
          // Invalid token, go to login
          await AuthUtils.clearAuthData();
          setInitialRoute('AuthScreen');
        }
      } else {
        // Not authenticated, go to login
        setInitialRoute('AuthScreen');
      }
    } catch (error) {
      console.error('Auth check error:', error);
      // On error, go to login
      setInitialRoute('AuthScreen');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: 'center', alignItems: 'center' }}>
        <ActivityIndicator size="large" color="#19376d" />
      </View>
    );
  }

  return (
    <NavigationContainer>
      <Stack.Navigator 
        initialRouteName={initialRoute}
        screenOptions={{ headerShown: false }}
      >
        <Stack.Screen name="AuthScreen" component={AuthScreen} />
        <Stack.Screen name="MainMenu" component={MainMenu} />
        <Stack.Screen name="DungeonSelect" component={DungeonSelect} />
        <Stack.Screen name="DailyChallenge" component={DailyChallenge} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
```

## 🛡️ Example: Auth Guard Hook

Create a custom hook for easy auth checking:

```javascript
// hooks/useAuth.js
import { useState, useEffect } from 'react';
import { useNavigation } from '@react-navigation/native';
import AuthUtils from '../authUtils';

export const useAuth = (requireAuth = true) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [authenticated, setAuthenticated] = useState(false);
  const navigation = useNavigation();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const isAuth = await AuthUtils.isAuthenticated();
      
      if (!isAuth && requireAuth) {
        navigation.replace('AuthScreen');
        return;
      }
      
      setAuthenticated(isAuth);
      
      if (isAuth) {
        const userData = await AuthUtils.getUserData();
        setUser(userData);
      }
    } catch (error) {
      console.error('Auth check error:', error);
      if (requireAuth) {
        navigation.replace('AuthScreen');
      }
    } finally {
      setLoading(false);
    }
  };

  const refresh = async () => {
    setLoading(true);
    await checkAuth();
  };

  return { user, loading, authenticated, refresh };
};

// Usage in a component:
import { useAuth } from './hooks/useAuth';

function MyScreen() {
  const { user, loading, authenticated } = useAuth();
  
  if (loading) {
    return <ActivityIndicator />;
  }
  
  return (
    <View>
      <Text>Welcome, {user?.email}</Text>
    </View>
  );
}
```

## 🔑 Token Refresh Example

The token refresh is automatic when using `AuthUtils.authenticatedRequest()`, but you can also manually refresh:

```javascript
import AuthUtils from './authUtils';

const refreshToken = async () => {
  try {
    const newAccessToken = await AuthUtils.refreshAccessToken();
    
    if (newAccessToken) {
      console.log('Token refreshed successfully');
      return true;
    } else {
      console.log('Token refresh failed, user needs to login');
      // Redirect to login
      navigation.replace('AuthScreen');
      return false;
    }
  } catch (error) {
    console.error('Token refresh error:', error);
    return false;
  }
};
```

## 📊 Example: User Profile Screen

```javascript
import React, { useState, useEffect } from 'react';
import { View, Text, TouchableOpacity, ActivityIndicator, Alert } from 'react-native';
import AuthUtils from './authUtils';
import styles from './Styles';

function ProfileScreen({ navigation }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      // Get fresh profile from backend
      const profile = await AuthUtils.getCurrentUserProfile();
      
      if (profile) {
        setUser(profile);
      } else {
        navigation.replace('AuthScreen');
      }
    } catch (error) {
      console.error('Error loading profile:', error);
      Alert.alert('Error', 'Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadProfile();
    setRefreshing(false);
  };

  if (loading) {
    return (
      <View style={styles.container}>
        <ActivityIndicator size="large" color="#19376d" />
      </View>
    );
  }

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Profile</Text>
      
      {user && (
        <View style={styles.headerBox}>
          <Text style={styles.headerText}>Email: {user.email}</Text>
          <Text style={styles.headerSubText}>ID: {user.id}</Text>
          <Text style={styles.headerSubText}>Status: {user.status}</Text>
          <Text style={styles.headerSubText}>
            Member since: {new Date(user.created_at).toLocaleDateString()}
          </Text>
        </View>
      )}
      
      <TouchableOpacity 
        style={styles.button}
        onPress={handleRefresh}
        disabled={refreshing}
      >
        <Text style={styles.buttonText}>
          {refreshing ? 'Refreshing...' : 'Refresh'}
        </Text>
      </TouchableOpacity>
      
      <TouchableOpacity 
        style={styles.button}
        onPress={() => navigation.goBack()}
      >
        <Text style={styles.buttonText}>Back</Text>
      </TouchableOpacity>
    </View>
  );
}

export default ProfileScreen;
```

## 🎯 Best Practices

1. **Always check authentication** before making protected API calls
2. **Use `AuthUtils.authenticatedRequest()`** for automatic token refresh
3. **Handle auth errors gracefully** by redirecting to login
4. **Cache user data** but refresh when needed
5. **Clear auth data on logout** completely
6. **Show loading states** during auth checks
7. **Use try-catch blocks** for all async auth operations
8. **Test token expiration** by manually expiring tokens
9. **Log auth events** for debugging
10. **Keep tokens secure** - never log them in production

## 🚨 Error Handling Patterns

```javascript
// Pattern 1: Redirect to login on auth failure
try {
  await AuthUtils.authenticatedRequest(apiCall);
} catch (error) {
  if (error.message.includes('Authentication failed')) {
    navigation.replace('AuthScreen');
  } else {
    Alert.alert('Error', error.message);
  }
}

// Pattern 2: Retry with refresh
try {
  await makeApiCall();
} catch (error) {
  if (error.message.includes('401')) {
    const refreshed = await AuthUtils.refreshAccessToken();
    if (refreshed) {
      await makeApiCall(); // Retry
    } else {
      navigation.replace('AuthScreen');
    }
  }
}

// Pattern 3: Silent fail with fallback
try {
  const profile = await AuthUtils.getCurrentUserProfile();
  setUser(profile);
} catch (error) {
  // Use cached data as fallback
  const cachedUser = await AuthUtils.getUserData();
  if (cachedUser) {
    setUser(cachedUser);
  }
}
```

These examples should help you implement authentication throughout your app!

