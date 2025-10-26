import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  TouchableOpacity,
  ActivityIndicator,
  Alert,
  StyleSheet,
} from 'react-native';
import { RunService } from '../services';
import styles from '../styles/Styles';

const QUESTION_TIME_LIMIT = 30; // seconds per question

function RunGameplay({ navigation, route }) {
  const { dungeonId, dungeonName, dungeonCategory } = route.params || {};
  
  // Run state
  const [runData, setRunData] = useState(null);
  const [questions, setQuestions] = useState([]);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [selectedAnswer, setSelectedAnswer] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  // Game state
  const [score, setScore] = useState(0);
  const [lives, setLives] = useState(3);
  const [streak, setStreak] = useState(0);
  const [maxStreak, setMaxStreak] = useState(0);
  const [timer, setTimer] = useState(QUESTION_TIME_LIMIT);
  const [turnData, setTurnData] = useState([]);
  const [scoresData, setScoresData] = useState([]);

  // Initialize run
  useEffect(() => {
    initializeRun();
  }, []);

  // Timer countdown
  useEffect(() => {
    if (!isLoading && !isSubmitting && timer > 0) {
      const interval = setInterval(() => {
        setTimer((prev) => prev - 1);
      }, 1000);
      return () => clearInterval(interval);
    } else if (timer === 0 && !isSubmitting) {
      // Time's up, treat as wrong answer
      handleAnswerSubmit(null, true);
    }
  }, [timer, isLoading, isSubmitting]);

  const initializeRun = async () => {
    try {
      setIsLoading(true);
      console.log('Initializing run for dungeon:', dungeonId);
      
      // Start run
      const run = await RunService.startRun(dungeonId, 1, {
        device: 'mobile',
        version: '1.0.0',
      });
      
      console.log('Run started:', run);
      setRunData(run);

      // Get questions
      const questionsData = await RunService.getQuestionsForRun(
        dungeonId,
        run.seed,
        10, // 10 questions per run
        1   // floor number
      );
      
      console.log('Questions received:', questionsData?.length || 0);
      
      // Ensure questionsData is an array
      const questions = Array.isArray(questionsData) ? questionsData : [];
      
      if (questions.length === 0) {
        throw new Error('No questions available for this dungeon');
      }
      
      setQuestions(questions);
      setIsLoading(false);
    } catch (error) {
      console.error('Failed to initialize run:', error);
      setIsLoading(false);
      Alert.alert(
        'Error',
        error.message || 'Failed to start dungeon run. Please try again.',
        [{ text: 'OK', onPress: () => navigation.goBack() }]
      );
    }
  };

  const handleAnswerSelect = (answerIndex) => {
    if (selectedAnswer === null && !isSubmitting) {
      setSelectedAnswer(answerIndex);
    }
  };

  const handleAnswerSubmit = async (answerIndex = selectedAnswer, timedOut = false) => {
    if (isSubmitting) return;
    
    setIsSubmitting(true);
    const question = questions[currentQuestionIndex];
    const answerTime = timedOut ? QUESTION_TIME_LIMIT : QUESTION_TIME_LIMIT - timer;
    
    // Validate answer with backend for real-time feedback
    let isCorrect = false;
    
    if (!timedOut) {
      try {
        const validation = await RunService.validateAnswer(
          runData.id,
          question.id,
          answerIndex
        );
        isCorrect = validation.is_correct;
      } catch (error) {
        console.error('Failed to validate answer:', error);
        // If validation fails, assume incorrect to be safe
        isCorrect = false;
      }
    }

    // Calculate points based on actual correctness
    let points = 0;
    let timeBonus = 0;
    let streakBonus = 0;

    if (isCorrect) {
      // Base points by difficulty
      const basePoints = {
        easy: 100,
        medium: 150,
        hard: 200,
      }[question.difficulty] || 100;

      // Time bonus (faster = more points, max 50%)
      timeBonus = Math.floor(basePoints * 0.5 * (timer / QUESTION_TIME_LIMIT));
      
      // Streak bonus (10% per streak, max 100%)
      streakBonus = Math.floor(basePoints * Math.min(streak * 0.1, 1.0));

      points = basePoints + timeBonus + streakBonus;

      setScore((prev) => prev + points);
      setStreak((prev) => prev + 1);
      setMaxStreak((prev) => Math.max(prev, streak + 1));
    } else {
      setLives((prev) => prev - 1);
      setStreak(0);
    }

    // Record turn data
    const turn = {
      i: currentQuestionIndex,
      qid: question.id,
      a: answerIndex ?? -1,
      c: isCorrect,
      t: Math.floor(answerTime * 1000),
      ts: Date.now(),
      h: await RunService.calculateTurnSignature(
        {
          i: currentQuestionIndex,
          qid: question.id,
          a: answerIndex ?? -1,
        },
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

    // Check if game over
    if (lives - (isCorrect ? 0 : 1) <= 0) {
      // Game over
      await completeRun(newTurnData, newScoresData);
    } else if (currentQuestionIndex >= questions.length - 1) {
      // Completed all questions
      await completeRun(newTurnData, newScoresData);
    } else {
      // Next question
      setTimeout(() => {
        setCurrentQuestionIndex((prev) => prev + 1);
        setSelectedAnswer(null);
        setTimer(QUESTION_TIME_LIMIT);
        setIsSubmitting(false);
      }, 1000);
    }
  };

  const completeRun = async (finalTurnData, finalScoresData) => {
    try {
      const signature = await RunService.calculateAggregateSignature(
        finalTurnData,
        runData.session_token
      );

      const result = await RunService.submitRun(
        runData.id,
        finalTurnData,
        finalScoresData,
        signature
      );

      // Use backend's validated results, not frontend's optimistic scores
      const validatedScores = result.summary?.scores || [];
      const actualCorrectCount = validatedScores.filter(s => s.is_correct).length;
      const actualScore = result.total_score || 0;

      // Navigate to results screen with ACTUAL results from backend
      navigation.replace('RunResults', {
        runData: result,
        score: actualScore,
        questionsAnswered: finalTurnData.length,
        correctAnswers: actualCorrectCount,
        maxStreak,
        dungeonName,
      });
    } catch (error) {
      console.error('Failed to submit run:', error);
      Alert.alert(
        'Error',
        'Failed to submit run results. Your progress may be lost.',
        [
          { text: 'Try Again', onPress: () => completeRun(finalTurnData, finalScoresData) },
          { text: 'Cancel', onPress: () => navigation.goBack() },
        ]
      );
    }
  };

  const handleAbandon = () => {
    Alert.alert(
      'Abandon Run?',
      'Are you sure you want to abandon this run? Your progress will be lost.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Abandon',
          style: 'destructive',
          onPress: async () => {
            try {
              if (runData) {
                await RunService.abandonRun(runData.id);
              }
              navigation.goBack();
            } catch (error) {
              console.error('Failed to abandon run:', error);
              navigation.goBack();
            }
          },
        },
      ]
    );
  };

  if (isLoading) {
    return (
      <View style={[styles.container, { justifyContent: 'center' }]}>
        <ActivityIndicator size="large" color="#19376d" />
        <Text style={[styles.headerText, { marginTop: 20 }]}>
          Loading Dungeon...
        </Text>
      </View>
    );
  }

  // Safety checks
  if (!questions || questions.length === 0) {
    return (
      <View style={[styles.container, { justifyContent: 'center', padding: 20 }]}>
        <Text style={[styles.headerText, { marginBottom: 20, textAlign: 'center' }]}>
          No questions available
        </Text>
        <TouchableOpacity
          style={[styles.playButton, { backgroundColor: '#19376d' }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.playText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  const currentQuestion = questions[currentQuestionIndex];
  
  if (!currentQuestion) {
    return (
      <View style={[styles.container, { justifyContent: 'center', padding: 20 }]}>
        <Text style={[styles.headerText, { marginBottom: 20, textAlign: 'center' }]}>
          Error loading question
        </Text>
        <TouchableOpacity
          style={[styles.playButton, { backgroundColor: '#19376d' }]}
          onPress={() => navigation.goBack()}
        >
          <Text style={styles.playText}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }
  
  const progress = ((currentQuestionIndex + 1) / questions.length) * 100;

  return (
    <View style={gameStyles.container}>
      {/* Header */}
      <View style={gameStyles.header}>
        <View style={gameStyles.headerRow}>
          <TouchableOpacity
            style={gameStyles.abandonButton}
            onPress={handleAbandon}
          >
            <Text style={gameStyles.abandonText}>✕</Text>
          </TouchableOpacity>
          
          <View style={gameStyles.dungeonInfo}>
            <Text style={gameStyles.dungeonName}>{dungeonName}</Text>
            <Text style={gameStyles.questionProgress}>
              Question {currentQuestionIndex + 1} / {questions.length}
            </Text>
          </View>
          
          <View style={gameStyles.placeholder} />
        </View>

        {/* Progress bar */}
        <View style={gameStyles.progressBarContainer}>
          <View
            style={[gameStyles.progressBar, { width: `${progress}%` }]}
          />
        </View>
      </View>

      {/* Stats Bar */}
      <View style={gameStyles.statsBar}>
        <View style={gameStyles.stat}>
          <Text style={gameStyles.statLabel}>Score</Text>
          <Text style={gameStyles.statValue}>{score}</Text>
        </View>
        
        <View style={gameStyles.stat}>
          <Text style={gameStyles.statLabel}>Lives</Text>
          <Text style={gameStyles.statValue}>{'❤️'.repeat(lives)}</Text>
        </View>
        
        <View style={gameStyles.stat}>
          <Text style={gameStyles.statLabel}>Streak</Text>
          <Text style={gameStyles.statValue}>{streak}🔥</Text>
        </View>
        
        <View style={gameStyles.stat}>
          <Text style={gameStyles.statLabel}>Time</Text>
          <Text style={[gameStyles.statValue, timer <= 5 && gameStyles.urgentTime]}>
            {timer}s
          </Text>
        </View>
      </View>

      {/* Question */}
      <View style={gameStyles.questionContainer}>
        <Text style={gameStyles.difficulty}>{currentQuestion.difficulty.toUpperCase()}</Text>
        <Text style={gameStyles.questionText}>{currentQuestion.prompt}</Text>
      </View>

      {/* Answers */}
      <View style={gameStyles.answersContainer}>
        {currentQuestion.choices.map((choice, index) => {
          const isSelected = selectedAnswer === index;

          return (
            <TouchableOpacity
              key={index}
              style={[
                gameStyles.answerButton,
                isSelected && gameStyles.selectedAnswer,
              ]}
              onPress={() => handleAnswerSelect(index)}
              disabled={isSubmitting}
            >
              <Text style={gameStyles.answerLetter}>
                {String.fromCharCode(65 + index)})
              </Text>
              <Text
                style={[
                  gameStyles.answerText,
                  isSelected && gameStyles.selectedAnswerText,
                ]}
              >
                {choice}
              </Text>
            </TouchableOpacity>
          );
        })}
      </View>

      {/* Submit Button */}
      <TouchableOpacity
        style={[
          gameStyles.submitButton,
          selectedAnswer === null && gameStyles.submitButtonDisabled,
        ]}
        onPress={() => handleAnswerSubmit()}
        disabled={selectedAnswer === null || isSubmitting}
      >
        <Text style={gameStyles.submitButtonText}>
          {isSubmitting ? 'Processing...' : 'Submit Answer'}
        </Text>
      </TouchableOpacity>
    </View>
  );
}

const gameStyles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0b2447',
  },
  header: {
    paddingHorizontal: 16,
    paddingTop: 12,
    paddingBottom: 8,
    backgroundColor: '#19376d',
  },
  headerRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 8,
  },
  abandonButton: {
    width: 40,
    height: 40,
    borderRadius: 20,
    backgroundColor: '#a5243d',
    justifyContent: 'center',
    alignItems: 'center',
  },
  abandonText: {
    color: '#fff',
    fontSize: 24,
    fontWeight: 'bold',
  },
  dungeonInfo: {
    alignItems: 'center',
  },
  dungeonName: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  questionProgress: {
    color: '#a0c1d1',
    fontSize: 14,
  },
  placeholder: {
    width: 40,
  },
  progressBarContainer: {
    height: 8,
    backgroundColor: '#0b2447',
    borderRadius: 4,
    overflow: 'hidden',
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#4a90e2',
    borderRadius: 4,
  },
  statsBar: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#19376d',
    borderBottomWidth: 2,
    borderBottomColor: '#0b2447',
  },
  stat: {
    alignItems: 'center',
    flex: 1,
  },
  statLabel: {
    color: '#a0c1d1',
    fontSize: 11,
    marginBottom: 2,
  },
  statValue: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  urgentTime: {
    color: '#ff4444',
  },
  questionContainer: {
    paddingHorizontal: 16,
    paddingVertical: 14,
    backgroundColor: '#19376d',
    marginHorizontal: 12,
    marginTop: 8,
    marginBottom: 6,
    borderRadius: 10,
    minHeight: 80,
    maxHeight: 120,
    justifyContent: 'center',
  },
  difficulty: {
    color: '#4a90e2',
    fontSize: 10,
    fontWeight: 'bold',
    marginBottom: 6,
    textTransform: 'uppercase',
  },
  questionText: {
    color: '#fff',
    fontSize: 15,
    lineHeight: 20,
    fontWeight: '500',
  },
  answersContainer: {
    flex: 1,
    paddingHorizontal: 12,
    paddingTop: 4,
    paddingBottom: 8,
  },
  answerButton: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#19376d',
    paddingVertical: 10,
    paddingHorizontal: 12,
    borderRadius: 8,
    marginBottom: 8,
    borderWidth: 2,
    borderColor: '#19376d',
    minHeight: 48,
  },
  selectedAnswer: {
    borderColor: '#4a90e2',
    backgroundColor: '#1a3d5c',
  },
  correctAnswer: {
    borderColor: '#4caf50',
    backgroundColor: '#1b5e20',
  },
  wrongAnswer: {
    borderColor: '#f44336',
    backgroundColor: '#5e1b1b',
  },
  answerLetter: {
    color: '#4a90e2',
    fontSize: 14,
    fontWeight: 'bold',
    marginRight: 8,
    width: 20,
  },
  answerText: {
    color: '#fff',
    fontSize: 14,
    flex: 1,
    flexWrap: 'wrap',
    lineHeight: 18,
  },
  selectedAnswerText: {
    fontWeight: 'bold',
  },
  submitButton: {
    backgroundColor: '#4a90e2',
    paddingVertical: 12,
    paddingHorizontal: 20,
    marginHorizontal: 12,
    marginTop: 6,
    marginBottom: 10,
    borderRadius: 10,
    alignItems: 'center',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.25,
    shadowRadius: 4,
    elevation: 5,
  },
  submitButtonDisabled: {
    backgroundColor: '#2c5f8d',
    opacity: 0.5,
  },
  submitButtonText: {
    color: '#fff',
    fontSize: 15,
    fontWeight: 'bold',
    letterSpacing: 0.5,
  },
});

export default RunGameplay;

