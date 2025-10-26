/**
 * Configuration file for API endpoints and app settings
 */
import { Platform } from 'react-native';

// API Configuration
// For local development:
// - Android emulator uses 10.0.2.2 to access host machine's localhost
// - iOS simulator uses localhost directly
// - Physical devices need your computer's local IP address (e.g., 192.168.1.X)
const getApiBaseUrl = () => {
  if (__DEV__) {
    // Development environment
    if (Platform.OS === 'android') {
      // Android emulator
      return 'http://10.0.2.2:8000';
    } else {
      // iOS simulator or other platforms
      return 'http://localhost:8000';
    }
  } else {
    // Production environment
    return 'https://your-production-url.com';
  }
};

const API_BASE_URL = getApiBaseUrl();
const API_TIMEOUT = 10000; // 10 seconds

export { API_BASE_URL, API_TIMEOUT };

