# 📝 Test Questions & Answers Reference

Quick reference for testing gameplay - know the correct answers to verify scoring works!

---

## 🏛️ History Questions

### Question 1
**Q:** Which ancient civilization built the pyramids of Giza?  
**Choices:** Romans | **Egyptians** | Greeks | Babylonians  
**Answer:** **Egyptians** (Choice 2)  
**Difficulty:** Easy

### Question 2
**Q:** Who was the first emperor of Rome?  
**Choices:** Julius Caesar | **Augustus** | Nero | Caligula  
**Answer:** **Augustus** (Choice 2)  
**Difficulty:** Medium

### Question 3
**Q:** In what year did World War II end?  
**Choices:** 1943 | 1944 | **1945** | 1946  
**Answer:** **1945** (Choice 3)  
**Difficulty:** Easy

### Question 4
**Q:** Which empire was ruled by Genghis Khan?  
**Choices:** Ottoman | **Mongol** | Persian | Roman  
**Answer:** **Mongol** (Choice 2)  
**Difficulty:** Medium

---

## ⚽ Sports Questions

### Question 1
**Q:** In which sport would you perform a slam dunk?  
**Choices:** Soccer | Tennis | **Basketball** | Volleyball  
**Answer:** **Basketball** (Choice 3)  
**Difficulty:** Easy

### Question 2
**Q:** How many players are on a soccer team?  
**Choices:** 9 | 10 | **11** | 12  
**Answer:** **11** (Choice 3)  
**Difficulty:** Easy

### Question 3
**Q:** Which country has won the most FIFA World Cups?  
**Choices:** Germany | Argentina | **Brazil** | Italy  
**Answer:** **Brazil** (Choice 3)  
**Difficulty:** Medium

---

## 🎵 Music Questions

### Question 1
**Q:** Which composer wrote "The Four Seasons"?  
**Choices:** Mozart | Bach | **Vivaldi** | Beethoven  
**Answer:** **Vivaldi** (Choice 3)  
**Difficulty:** Medium

### Question 2
**Q:** How many strings does a standard guitar have?  
**Choices:** 4 | 5 | **6** | 7  
**Answer:** **6** (Choice 3)  
**Difficulty:** Easy

### Question 3
**Q:** Which band sang "Bohemian Rhapsody"?  
**Choices:** The Beatles | **Queen** | Led Zeppelin | Pink Floyd  
**Answer:** **Queen** (Choice 2)  
**Difficulty:** Easy

---

## 📺 Pop Culture Questions

### Question 1
**Q:** What TV show featured the characters Ross, Rachel, and Monica?  
**Choices:** Seinfeld | **Friends** | Cheers | Frasier  
**Answer:** **Friends** (Choice 2)  
**Difficulty:** Easy

### Question 2
**Q:** Which movie won the Oscar for Best Picture in 1994?  
**Choices:** Pulp Fiction | **Forrest Gump** | The Shawshank Redemption | The Lion King  
**Answer:** **Forrest Gump** (Choice 2)  
**Difficulty:** Hard

### Question 3
**Q:** Who played Iron Man in the Marvel Cinematic Universe?  
**Choices:** Chris Evans | Chris Hemsworth | **Robert Downey Jr.** | Mark Ruffalo  
**Answer:** **Robert Downey Jr.** (Choice 3)  
**Difficulty:** Easy

---

## 🎯 Testing Strategies

### High Score Run
Answer all questions correctly to test:
- Maximum score calculation
- Perfect run completion
- Top leaderboard placement

**Recommended for:** First test run

### Mixed Score Run
Answer some correct, some incorrect to test:
- Partial scoring
- Streak mechanics (if implemented)
- Average score calculation

**Recommended for:** Second test run

### Low Score Run (Optional)
Answer most questions incorrectly to test:
- Low score handling
- Lives system (if implemented)
- Retry functionality

**Recommended for:** Third test run

---

## 📊 Expected Scoring

**Note:** Exact scoring depends on your implementation. Typical scoring:

- **Correct Answer:** +100 points (base)
- **Speed Bonus:** +0-50 points (if faster)
- **Streak Bonus:** +10 points per streak (if consecutive correct)
- **Difficulty Multiplier:** 
  - Easy: 1x
  - Medium: 1.5x
  - Hard: 2x

### Sample Perfect Runs

**History Dungeon (4 questions):**
- All correct: ~400-500 points
- Depends on difficulty mix

**Sports Dungeon (3 questions):**
- All correct: ~300-400 points

**Music Dungeon (3 questions):**
- All correct: ~300-400 points

**Pop Culture (3 questions):**
- All correct: ~300-450 points (has 1 hard question)

---

## 🧪 Test Scenarios

### Scenario 1: Perfect Player
1. Complete History dungeon - all correct
2. Complete Sports dungeon - all correct
3. Check leaderboard - should be ranked high
4. Total score: ~1000-1500 points

### Scenario 2: Casual Player
1. Complete 2 dungeons with ~60% correct
2. Check leaderboard - moderate rank
3. Total score: ~400-600 points

### Scenario 3: Difficulty Testing
1. Complete Pop Culture (has hard question)
2. Get hard question wrong, others right
3. Verify scoring reflects difficulty

---

## 💡 Tips for Testing

### Verify Scoring Logic
- [ ] Correct answer increases score
- [ ] Incorrect answer doesn't increase (or decreases if lives used)
- [ ] Final score matches sum of question scores
- [ ] Leaderboard total = sum of all completed runs

### Test Edge Cases
- [ ] Answer all questions in < 1 second (if timer)
- [ ] Let timer run out (if applicable)
- [ ] Answer same question different ways in different runs
- [ ] Complete same dungeon multiple times

### Check Data Persistence
- [ ] Scores persist after app restart
- [ ] History shows all runs
- [ ] Leaderboard maintains rankings

---

## 📱 Quick Testing Script

**5-Minute Test:**
1. Start History dungeon
2. Answer all 4 questions correctly (use this sheet!)
3. Check score on results
4. View Run History
5. Check All-Time Leaderboard
6. Done! ✅

**15-Minute Full Test:**
1. Complete all 4 dungeons
2. Mix correct/incorrect answers
3. Check History after each
4. Check all 3 leaderboard scopes
5. Verify stats update correctly
6. Done! ✅

---

## 🎮 Have Fun Testing!

Remember: You're not just testing - you're the first player of your game! 

**Pro tip:** Try to beat your own high score across multiple test runs! 🏆

