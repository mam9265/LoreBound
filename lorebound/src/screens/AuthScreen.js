import React, { useState } from 'react';
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  KeyboardAvoidingView,
  Platform,
  Alert,
  ActivityIndicator,
  useWindowDimensions,
  ScrollView,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import styles from '../styles/Styles';
import ApiService from '../services/api';

function AuthScreen({ navigation }) {
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const { width, height } = useWindowDimensions();
  const isLandscape = width > height;

  const handleLogin = async () => {
    if (!email || !password) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }
    setLoading(true);
    try {
      console.log('[AUTH] Starting login...');
      const response = await ApiService.login(email, password);
      console.log('[AUTH] Login response received');
      
      await AsyncStorage.setItem('access_token', response.tokens.access_token);
      await AsyncStorage.setItem('refresh_token', response.tokens.refresh_token);
      await AsyncStorage.setItem('user_data', JSON.stringify(response.user));
      console.log('[AUTH] Tokens saved to storage');
      
      Alert.alert('Success', 'Login successful!', [
        { 
          text: 'OK', 
          onPress: () => {
            console.log('[AUTH] Navigating to MainMenu...');
            navigation.navigate('MainMenu');
          } 
        },
      ]);
    } catch (error) {
      console.error('[AUTH] Login error:', error);
      Alert.alert('Login Failed', error.message || 'Login failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async () => {
    if (!email || !username || !password || !confirmPassword) {
      Alert.alert('Error', 'Please fill in all fields');
      return;
    }
    if (password !== confirmPassword) {
      Alert.alert('Error', 'Passwords do not match');
      return;
    }
    if (password.length < 6) {
      Alert.alert('Error', 'Password must be at least 6 characters long');
      return;
    }
    setLoading(true);
    try {
      const response = await ApiService.register(email, username, password);
      await AsyncStorage.setItem('access_token', response.tokens.access_token);
      await AsyncStorage.setItem('refresh_token', response.tokens.refresh_token);
      await AsyncStorage.setItem('user_data', JSON.stringify(response.user));
      Alert.alert('Success', 'Registration successful!', [
        { text: 'OK', onPress: () => navigation.navigate('MainMenu') },
      ]);
    } catch (error) {
      Alert.alert('Registration Failed', error.message || 'Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const toggleAuthMode = () => {
    setIsLogin(!isLogin);
    setEmail('');
    setUsername('');
    setPassword('');
    setConfirmPassword('');
  };

  return (
    <KeyboardAvoidingView
      style={[
        styles.authContainer,
        isLandscape && styles.authContainerLandscape,
      ]}
      behavior={Platform.OS === 'ios' ? 'padding' : undefined}
    >
      {/* LEFT SIDE - Title */}
      <View style={[
        styles.authTitleContainer,
        isLandscape ? styles.authTitleContainerLandscape : null,
      ]}>
        <Text style={styles.authTitle}>
          <Text style={styles.lore}>Lore</Text>
          <Text style={styles.bound}>Bound</Text>
        </Text>
        <Text style={styles.authSubtitle}>
          {isLogin ? 'Welcome Back!' : 'Create Your Account'}
        </Text>
      </View>

      {/* RIGHT SIDE - Form */}
      <ScrollView
        contentContainerStyle={[
          styles.authScrollContent,
          isLandscape && styles.authScrollContentLandscape,
        ]}
        keyboardShouldPersistTaps="handled"
      >
        <View style={[
          styles.authFormContainer,
          isLandscape && styles.authFormContainerLandscape,
        ]}>
          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Email</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your email"
              placeholderTextColor="#999"
              value={email}
              onChangeText={setEmail}
              keyboardType="email-address"
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          {!isLogin && (
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Username</Text>
              <TextInput
                style={styles.input}
                placeholder="Choose a username"
                placeholderTextColor="#999"
                value={username}
                onChangeText={setUsername}
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>
          )}

          <View style={styles.inputContainer}>
            <Text style={styles.inputLabel}>Password</Text>
            <TextInput
              style={styles.input}
              placeholder="Enter your password"
              placeholderTextColor="#999"
              value={password}
              onChangeText={setPassword}
              secureTextEntry
              autoCapitalize="none"
              autoCorrect={false}
            />
          </View>

          {!isLogin && (
            <View style={styles.inputContainer}>
              <Text style={styles.inputLabel}>Confirm Password</Text>
              <TextInput
                style={styles.input}
                placeholder="Confirm your password"
                placeholderTextColor="#999"
                value={confirmPassword}
                onChangeText={setConfirmPassword}
                secureTextEntry
                autoCapitalize="none"
                autoCorrect={false}
              />
            </View>
          )}

          <TouchableOpacity
            style={[styles.authButton, loading && styles.authButtonDisabled]}
            onPress={isLogin ? handleLogin : handleRegister}
            disabled={loading}
          >
            {loading ? (
              <ActivityIndicator color="#FFF" />
            ) : (
              <Text style={styles.authButtonText}>{isLogin ? 'Login' : 'Register'}</Text>
            )}
          </TouchableOpacity>

          <View style={styles.authToggleContainer}>
            <Text style={styles.authToggleText}>
              {isLogin ? "Don't have an account? " : 'Already have an account? '}
            </Text>
            <TouchableOpacity onPress={toggleAuthMode}>
              <Text style={styles.authToggleLink}>
                {isLogin ? 'Register' : 'Login'}
              </Text>
            </TouchableOpacity>
          </View>
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

export default AuthScreen;
