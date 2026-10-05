# 💭 Reflection: Game Glitch Investigator

Answer each question in 3 to 5 sentences. Be specific and honest about what actually happened while you worked. This is about your process, not trying to sound perfect.

## 1. What was broken when you started?

- What did the game look like the first time you ran it?
The game looked like a normal game of guess from range 1 to 100. The first input I put in was 1 but the hint says go lower as 100 says go higher. Since the number is 75, the numbers lower says its lower as higher says higher. Therefore, the inequalities are incorrect. When I start a new game, the game does not reset but the score reset to -5

- List at least two concrete bugs you noticed at the start  
  1. Inequalities are incorrect
  2. I found was that new Game button does not reset to a new game.
  3. When I enter a non-digit, it goes to negative attempts left once there are not more attempts

**Bug Reproduction Log**

Document at least 3 bugs you found. Add rows as needed.

| Input | Expected Behavior | Actual Behavior | Console Output / Error |
|-------|-------------------|-----------------|------------------------|
|1 as input|Expected to go higher|Hint says go higher|None|
|Click new game|Expected a new game develop|New game started but does not allow any input|None|
|R|Not allow non-digit message and not take it as an attempt|Allowed it multiple times to get a negative attempts left|None|

---

## 2. How did you use AI as a teammate?

- Which AI tools did you use on this project (for example: ChatGPT, Gemini, Copilot)?
I used Claude 
- Give one example of an AI suggestion that was correct (including what the AI suggested and how you verified the result).
The conversion of string which causes the inequality of lexicographic instead of int.
- Give one example of an AI suggestion you did not accept as written (including what the AI suggested, why you rejected or changed it, and how you verified your version). It does not have to be a suggestion that was wrong: over-engineered, out of scope, harder to read, or a poor fit for this codebase all count.
I did not accept the how to reset the game but rearranging the methods.

---

## 3. Debugging and testing your fixes

- How did you decide whether a bug was really fixed?
When AI said the comparision is based on string and not digits, I knew that was one of the bug is really fixed.
- Describe at least one test you ran (manual or using pytest)  
  and what it showed you about your code.
  I ran the check_guess and it failed three tests. I realized the check_guess has not been fixed with High or Low. Once that was fixed, it was able to run the code with flying colors.
- Did AI help you design or understand any tests? How?
It helped me create some use cases that will cover all of the use cases.

---

## 4. What did you learn about Streamlit and state?

- How would you explain Streamlit "reruns" and session state to a friend who has never used Streamlit?
Streamlit is a Python framework that lets you quickly build and deploy interactive web applications, such as a website where users log in with their email and store information associated with their account.

---

## 5. Looking ahead: your developer habits

- What is one habit or strategy from this project that you want to reuse in future labs or projects?
  - This could be a testing habit, a prompting strategy, or a way you used Git.
  One habbit I learned was how to ask the right questions and do one degugging issues at a time. Also Git helps with the history if you want to go back to the changes to the previous strategy.
- What is one thing you would do differently next time you work with AI on a coding task?
Debug one issue at a time.
- In one or two sentences, describe how this project changed the way you think about AI generated code.
This helped me think that AI can assist issues that could happen and give use cases.

