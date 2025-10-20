import React from 'react';
import { View, Text, TouchableOpacity, ImageBackground, Image } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import styles from './src/styles/Styles';
import AuthScreen from './src/screens/AuthScreen';
import MainMenu from './src/screens/MainMenu';
import DailyChallenge from './src/screens/DailyChallenge';
import DungeonSelect from './src/screens/DungeonSelect';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Auth" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Auth" component={AuthScreen} />
        <Stack.Screen name="MainMenu" component={MainMenu} />
        <Stack.Screen name="DailyChallenge" component={DailyChallenge} />
        <Stack.Screen name="DungeonSelect" component={DungeonSelect} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
