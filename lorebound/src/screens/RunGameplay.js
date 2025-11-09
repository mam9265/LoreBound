// RunGameplay.js
import React, { useState, useEffect } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  StyleSheet,
  ImageBackground,
  Image,
} from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { RunService } from '../services';
import styles from '../styles/Styles';

// local sprites (used when characterCustomization saved colorIndex)
import RedKnight from '../assets/RedKnight.png';
import GreenKnight from '../assets/GreenKnight.png';
import BlueKnight from '../assets/BlueKnight.png';

// new names you requested
// background: OldDungeon.png
// enemy sprite: Wizard.png
const BACKGROUND = require('../assets/OldDungeon.png');
const WIZARD = require('../assets/Wizard.png');

const QUESTION_TIME_LIMIT = 30;

function RunGameplay({ navigation, route }) {
  const {
    dungeonId,
    dungeonName,
    dungeonCategory,
    isDailyChallenge = false,
    challengeModifiers = {},
    runData: preLoadedRunData = null,
    questions: preLoadedQuestions = null,
  } = route.params || {};

  // Run state
  const [runData, setRunData] = useState(preLoadedRunData);
  const [questions, setQuestions] = useState(preLoadedQuestions || []);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [isLoading, setIsLoading] = useState(!preLoadedRunData || !preLoadedQuestions);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Game state
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [streak, setStreak] = useState(0);
  const [maxStreak, setMaxStreak] = useState(0);
  const [correctCount, setCorrectCount] = useState(0);
  const [timer, setTimer] = useState(QUESTION_TIME_LIMIT);
  const [turnData, setTurnData] = useState([]);
  const [scoresData, setScoresData] = useState([]);

  // Avatar state: store an Image source (either require(...) or { uri: '...' })
  const [playerSpriteSource, setPlayerSpriteSource] = useState(RedKnight); // Default immediately

  // Load avatar / color index from cache first for instant display
  useEffect(() => {
    const loadAvatar = async () => {
      try {
        const sprites = [RedKnight, GreenKnight, BlueKnight];
        
        // Try to load cached color first (instant!)
        try {
          const { ProfileService } = await import('../services');
          const cachedColorIndex = await ProfileService.getCachedColorIndex();
          
          if (typeof cachedColorIndex === 'number') {
            const idx = Math.max(0, Math.min(cachedColorIndex, sprites.length - 1));
            setPlayerSpriteSource(sprites[idx]);
            console.log('[RunGameplay] Loaded knight color from cache (instant):', idx);
            return;
          }
          
          // If no cache, load from backend (will cache for next time)
          const profileData = await ProfileService.loadCharacterCustomization();
          if (profileData && typeof profileData.colorIndex === 'number') {
            const idx = Math.max(0, Math.min(profileData.colorIndex, sprites.length - 1));
            setPlayerSpriteSource(sprites[idx]);
            console.log('[RunGameplay] Loaded knight color from backend:', idx);
            return;
          }
        } catch (profileError) {
          console.warn('[RunGameplay] Could not load from profile:', profileError);
        }

        // Default to Red Knight (already set in state)
        console.log('[RunGameplay] Using default knight color (Red)');
      } catch (err) {
        console.warn('[RunGameplay] Error loading avatar:', err);
      }
    };

    loadAvatar();
    initializeRun();
  }, []);

  // Init run (kept identical logic)
  const initializeRun = async () => {
    if (preLoadedRunData && preLoadedQuestions && preLoadedQuestions.length > 0) {
      setIsLoading(false);
      return;
    }
    try {
      setIsLoading(true);
      const run = await RunService.startRun(dungeonId, 1, {
        device: 'mobile',
        version: '1.0.0',
        is_daily_challenge: isDailyChallenge,
      });
      setRunData(run);

      const questionsData = await RunService.getQuestionsForRun(
        dungeonId,
        run.seed,
        10,
        1
      );
      const arr = Array.isArray(questionsData) ? questionsData : [];
      if (arr.length === 0) throw new Error('No questions available for this dungeon');
      setQuestions(arr);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to initialize run:', error);
      setIsLoading(false);
      Alert.alert('Error', error.message || 'Failed to start dungeon run.', [
        { text: 'OK', onPress: () => navigation.goBack() },
      ]);
    }
  };

  // Timer countdown
  useEffect(() => {
    if (!isLoading && !isSubmitting && timer > 0) {
      const interval = setInterval(() => setTimer((p) => p - 1), 1000);
      return () => clearInterval(interval);
    } else if (timer === 0 && !isSubmitting) {
      handleAnswerSubmit(null, true);
    }
  }, [timer, isLoading, isSubmitting]);

  // Answer select
  const handleAnswerSelect = (answerIndex) => {
    if (!isSubmitting) setSelectedAnswer(answerIndex);
  };

  // Submit answer (kept same)
  const handleAnswerSubmit = async (answerIndex = selectedAnswer, timedOut = false) => {
    if (isSubmitting) return;
    setIsSubmitting(true);
    const question = questions[currentQuestionIndex];
    const answerTime = timedOut ? QUESTION_TIME_LIMIT : QUESTION_TIME_LIMIT - timer;
    let isCorrect = false;

    if (!timedOut) {
      try {
        const validation = await RunService.validateAnswer(runData.id, question.id, answerIndex);
        isCorrect = validation.is_correct;
      } catch (e) {
        console.error('Validation failed:', e);
        isCorrect = false;
      }
    }

    let points = 0;
    let timeBonus = 0;
    let streakBonus = 0;

    if (isCorrect) {
      const basePoints = { easy: 100, medium: 150, hard: 200 }[question.difficulty] || 100;
      timeBonus = Math.floor(basePoints * 0.5 * (timer / QUESTION_TIME_LIMIT));
      streakBonus = Math.floor(basePoints * Math.min(streak * 0.1, 1.0));
      points = basePoints + timeBonus + streakBonus;

      if (isDailyChallenge && challengeModifiers.points_multiplier) {
        points = Math.floor(points * challengeModifiers.points_multiplier);
      }

      setScore((p) => p + points);
      setStreak((s) => s + 1);
      setMaxStreak((m) => Math.max(m, streak + 1));
      setCorrectCount((c) => c + 1);
    } else {
      setLives((l) => l - 1);
      setStreak(0);
    }

    const turn = {
      i: currentQuestionIndex,
      qid: question.id,
      a: answerIndex ?? -1,
      c: isCorrect,
      t: Math.floor(answerTime * 1000),
      ts: Date.now(),
      h: await RunService.calculateTurnSignature(
        { i: currentQuestionIndex, qid: question.id, a: answerIndex ?? -1 },
        runData.session_token
      ),
    };

    const scoreEntry = {
      points,
      answer_time: answerTime,
      is_correct: isCorrect,
      streak_bonus: streakBonus,
      time_bonus: timeBonus,
    };

    const newTurnData = [...turnData, turn];
    const newScoresData = [...scoresData, scoreEntry];
    setTurnData(newTurnData);
    setScoresData(newScoresData);

    const newLives = lives - (isCorrect ? 0 : 1);
    const newCorrectCount = correctCount + (isCorrect ? 1 : 0);

    if (newLives <= 0) {
      await completeRun(newTurnData, newScoresData, false, newCorrectCount);
    } else if (currentQuestionIndex >= questions.length - 1) {
      await completeRun(newTurnData, newScoresData, true, newCorrectCount);
    } else {
      setTimeout(() => {
        setCurrentQuestionIndex((p) => p + 1);
        setSelectedAnswer(null);
        setTimer(QUESTION_TIME_LIMIT);
        setIsSubmitting(false);
      }, 900);
    }
  };

  const completeRun = async (finalTurnData, finalScoresData, isVictory = true, finalCorrectCount = correctCount) => {
    try {
      const signature = await RunService.calculateAggregateSignature(finalTurnData, runData.session_token);
      const result = await RunService.submitRun(
        runData.id, 
        finalTurnData, 
        finalScoresData, 
        signature, 
        isVictory,
        isDailyChallenge
      );
      const actualScore = result.total_score || score;
      navigation.replace('RunResults', {
        runData: result,
        score: actualScore,
        questionsAnswered: finalTurnData.length,
        correctAnswers: finalCorrectCount,
        maxStreak,
        dungeonName,
        isVictory,
        totalQuestions: questions.length,
        isDailyChallenge,
        challengeModifiers,
      });
    } catch (error) {
      console.error('Submit run failed:', error);
      Alert.alert('Error', 'Failed to submit run results.', [
        { text: 'Try Again', onPress: () => completeRun(finalTurnData, finalScoresData, isVictory, finalCorrectCount) },
        { text: 'Cancel', onPress: () => navigation.goBack() },
      ]);
    }
  };

  const handleAbandon = () => {
    Alert.alert('Abandon Run?', 'Your progress will be lost.', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Abandon',
        style: 'destructive',
        onPress: async () => {
          try {
            if (runData) await RunService.abandonRun(runData.id);
            navigation.goBack();
          } catch {
            navigation.goBack();
          }
        },
      },
    ]);
  };

  // Loading UI
  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator size="large" color="#19376d" />
        <Text style={[styles.headerText, { marginTop: 20 }]}>Loading Dungeon...</Text>
      </View>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  if (!currentQuestion) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <Text style={styles.headerText}>No questions available</Text>
      </View>
    );
  }

  return (
    <ImageBackground source={BACKGROUND} style={gameStyles.background} resizeMode="cover">
      {/* small cancel button in top-left */}
      <TouchableOpacity style={gameStyles.abandonButton} onPress={handleAbandon}>
        <Text style={gameStyles.abandonText}>✕</Text>
      </TouchableOpacity>

      {/* compact stats row */}
      <View style={gameStyles.statsRow}>
        <Text style={gameStyles.statText}>❤️ {lives}</Text>
        <Text style={gameStyles.statText}>🔥 {streak}</Text>
        <Text style={gameStyles.statText}>💯 {score}</Text>
        <Text style={[gameStyles.statText, timer <= 5 && gameStyles.urgentTime]}>{timer}s</Text>
      </View>

      {/* question displayed directly (no blue container) */}
      <Text style={gameStyles.questionText}>{currentQuestion.prompt}</Text>

      {/* Answers 2x2 grid */}
      <View style={gameStyles.answersGrid}>
        {currentQuestion.choices.map((choice, index) => {
          const isSelected = selectedAnswer === index;
          return (
            <TouchableOpacity
              key={index}
              style={[gameStyles.answerButton, isSelected && gameStyles.selectedAnswer]}
              onPress={() => handleAnswerSelect(index)}
              disabled={isSubmitting}
              activeOpacity={0.85}
            >
              <Text style={gameStyles.answerLetter}>{String.fromCharCode(65 + index)})</Text>
              <Text style={[gameStyles.answerText, isSelected && gameStyles.selectedAnswerText]}>
                {choice}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Sprites BELOW answers and ABOVE submit */}
      <View style={gameStyles.battleAreaBelowAnswers}>
        {/* player avatar left */}
        {playerSpriteSource ? (
          <Image source={playerSpriteSource} style={gameStyles.player} />
        ) : (
          <View style={gameStyles.placeholderPlayer}>
            <Text style={{ color: '#fff' }}>No Avatar</Text>
          </View>
        )}

        {/* wizard right */}
        <Image source={WIZARD} style={gameStyles.enemy} />
      </View>

      {/* Submit Button at bottom */}
      <TouchableOpacity
        style={[gameStyles.submitButton, (selectedAnswer === null || isSubmitting) && gameStyles.submitButtonDisabled]}
        onPress={() => handleAnswerSubmit()}
        disabled={selectedAnswer === null || isSubmitting}
      >
        <Text style={gameStyles.submitButtonText}>{isSubmitting ? 'Processing...' : 'Submit Answer'}</Text>
      </TouchableOpacity>
    </ImageBackground>
  );
}

const gameStyles = StyleSheet.create({
  background: {
    flex: 1,
    justifyContent: 'space-between',
    paddingVertical: 8,
  },

  /* small cancel button top-left */
  abandonButton: {
    position: 'absolute',
    top: 28,
    left: 12,
    width: 46,
    height: 46,
    borderRadius: 23,
    backgroundColor: '#a5243d',
    justifyContent: 'center',
    alignItems: 'center',
    zIndex: 30,
  },
  abandonText: { color: '#fff', fontSize: 26, fontWeight: '700' },

  /* compact stats row right under top area */
  statsRow: {
    marginTop: 8,
    marginHorizontal: 12,
    backgroundColor: 'rgba(25,55,109,0.85)',
    paddingVertical: 8,
    paddingHorizontal: 12,
    borderRadius: 8,
    flexDirection: 'row',
    justifyContent: 'space-around',
    alignItems: 'center',
  },
  statText: { color: '#fff', fontWeight: '600', fontSize: 14 },
  urgentTime: { color: '#ff4444' },

  /* Question text (no container) */
  questionText: {
    color: '#fff',
    fontSize: 16,
    textAlign: 'center',
    marginHorizontal: 18,
    fontWeight: '600',
  },

  /* Answers grid (2x2) */
  answersGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    marginHorizontal: 12,
    marginTop: 8,
    paddingHorizontal: 6,
  },
  answerButton: {
    width: '48%',
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: 'rgba(25,55,109,0.9)',
    borderRadius: 12,
    marginVertical: 8,
    paddingVertical: 12,
    paddingHorizontal: 12,
    borderWidth: 2,
    borderColor: '#19376d',
    minHeight: 56,
  },
  selectedAnswer: {
    borderColor: '#4a90e2',
    backgroundColor: '#1a3d5c',
  },
  answerLetter: {
    color: '#4a90e2',
    fontSize: 14,
    fontWeight: '700',
    marginRight: 8,
  },
  answerText: {
    color: '#fff',
    fontSize: 14,
    flexShrink: 1,
  },
  selectedAnswerText: { fontWeight: '700' },

  /* Sprites area under answers */
  battleAreaBelowAnswers: {
    marginHorizontal: 18,
    marginTop: 6,
    marginBottom: 8,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-end',
    height: 120,
  },
  player: {
    width: 110,
    height: 110,
    resizeMode: 'contain',
    borderRadius: 8,
    backgroundColor: 'rgba(0,0,0,0)', // keep transparent
  },
  placeholderPlayer: {
    width: 110,
    height: 110,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.06)',
    justifyContent: 'center',
    alignItems: 'center',
  },
  enemy: {
    width: 110,
    height: 110,
    resizeMode: 'contain',
  },

  /* Submit button */
  submitButton: {
    backgroundColor: '#4a90e2',
    paddingVertical: 12,
    marginHorizontal: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 14,
  },
  submitButtonDisabled: {
    opacity: 0.55,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 16,
    fontWeight: '700',
  },
});

export default RunGameplay;
