import React from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import styles from './Styles';


function DailyChallenge({ navigation  }) {
  return (
    <View style={styles.container}>
      <View style={styles.headerBox}>
        {/* Menu */}
        <Text style={styles.headerText}>Today’s Theme: Music</Text>
        <Text style={styles.headerSubText}>Time Until Next Challenge: 7 Hours</Text>
      </View>
      {/* Play Button */}
      <TouchableOpacity style={styles.playButton}>
        <Text style={styles.playText}>PLAY</Text>
      </TouchableOpacity>
      {/* Back Button */}
      <TouchableOpacity
        style={[styles.playButton, {backgroundColor: '#19376d', marginTop: 10 }]} onPress={() => navigation.goBack()}>
        <Text style={styles.playText}>BACK</Text>
      </TouchableOpacity>
    </View>
  );
}

export default DailyChallenge;