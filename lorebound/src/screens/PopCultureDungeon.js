import React from 'react';
import { View, Text, TouchableOpacity, Image } from 'react-native';
import styles from '../styles/Styles';


function PopCultureDungeon({ navigation  }) {
  return (
    <View style={styles.container}>
      <View style={styles.headerBox}>
        {/* Menu */}
        <Text style={styles.headerText}>POP CULTURE DUNGEON</Text>
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

export default PopCultureDungeon;