import React from 'react';
import { View, Text, TouchableOpacity, ImageBackground, Image } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import styles from './Styles';
import MainMenu from './MainMenu';
import DailyChallenge from './DailyChallenge';
import DungeonSelect from './DungeonSelect';
import CharacterCustomization from './CharacterCustomization';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="MainMenu" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="MainMenu" component={MainMenu} />
        <Stack.Screen name="DailyChallenge" component={DailyChallenge} />
        <Stack.Screen name="DungeonSelect" component={DungeonSelect} />
        <Stack.Screen name="CharacterCustomization" component={CharacterCustomization} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
