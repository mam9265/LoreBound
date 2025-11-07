import React from 'react';
import { View, Text, TouchableOpacity, ImageBackground, Image } from 'react-native';
import { NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import styles from './src/styles/Styles';
import AuthScreen from './src/screens/AuthScreen';
import MainMenu from './src/screens/MainMenu';
import DailyChallenge from './src/screens/DailyChallenge';
import DungeonSelect from './src/screens/DungeonSelect';
import SportDungeon from './src/screens/SportDungeon';
import MusicDungeon from './src/screens/MusicDungeon';
import HistoryDungeon from './src/screens/HistoryDungeon';
import BookDungeon from './src/screens/BookDungeon';
import PopCultureDungeon from './src/screens/PopCultureDungeon';
import AllAroundDungeon from './src/screens/AllAroundDungeon';
import CharacterCustomization from './src/screens/CharacterCustomization';
import Leaderboards from './src/screens/Leaderboard';
import RunGameplay from './src/screens/RunGameplay';
import RunGameplayDebug from './src/screens/RunGameplayDebug';
import RunResults from './src/screens/RunResults';
import RunHistory from './src/screens/RunHistory';

const Stack = createNativeStackNavigator();

export default function App() {
  return (
    <NavigationContainer>
      <Stack.Navigator initialRouteName="Auth" screenOptions={{ headerShown: false }}>
        <Stack.Screen name="Auth" component={AuthScreen} />
        <Stack.Screen name="MainMenu" component={MainMenu} />
        <Stack.Screen name="DailyChallenge" component={DailyChallenge} />
        <Stack.Screen name="DungeonSelect" component={DungeonSelect} />
        <Stack.Screen name="CharacterCustomization" component={CharacterCustomization} />
        <Stack.Screen name="Leaderboard" component={Leaderboards} />
        <Stack.Screen name="RunGameplay" component={RunGameplay} />
        <Stack.Screen name="SportDungeon" component={SportDungeon} />
        <Stack.Screen name="MusicDungeon" component={MusicDungeon} />
        <Stack.Screen name="HistoryDungeon" component={HistoryDungeon} />
        <Stack.Screen name="BookDungeon" component={BookDungeon} />
        <Stack.Screen name="PopCultureDungeon" component={PopCultureDungeon} />
        <Stack.Screen name="AllAroundDungeon" component={AllAroundDungeon} />
        <Stack.Screen name="RunResults" component={RunResults} />
        <Stack.Screen name="RunHistory" component={RunHistory} />
      </Stack.Navigator>
    </NavigationContainer>
  );
}