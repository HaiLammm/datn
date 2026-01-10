# Prompt Tuning Guide - Customizing AI Agent Prompts

Hướng dẫn chi tiết về cách customize và optimize system prompts cho các AI sub-agents.

## 📋 Table of Contents

1. [Understanding Prompts](#understanding-prompts)
2. [Prompt Engineering Principles](#prompt-engineering-principles)
3. [Tuning Process](#tuning-process)
4. [Agent-Specific Guidelines](#agent-specific-guidelines)
5. [Testing and Validation](#testing-and-validation)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Understanding Prompts

### What is a System Prompt?

System prompt là instruction template định nghĩa:
- **Role & Persona**: Agent đóng vai trò gì, tính cách như thế nào
- **Task Definition**: Agent cần làm gì
- **Output Format**: Kết quả trả về có cấu trúc như thế nào
- **Constraints**: Các quy tắc, giới hạn cần tuân thủ
- **Examples**: Ví dụ minh họa (few-shot learning)

### Prompt Structure

```
┌─────────────────────────────────────────────┐
│  1. ROLE & PERSONA                          │  ← Who the agent is
│     "You are a Senior Technical Interviewer"│
├─────────────────────────────────────────────┤
│  2. TASK DEFINITION                         │  ← What to do
│     "Your task is to evaluate..."           │
├─────────────────────────────────────────────┤
│  3. INPUT SPECIFICATION                     │  ← What inputs to expect
│     "You will receive: JD, CV, Level"       │
├─────────────────────────────────────────────┤
│  4. THINKING PROCESS                        │  ← How to think
│     "First analyze..., then consider..."    │
├─────────────────────────────────────────────┤
│  5. OUTPUT FORMAT                           │  ← Expected output
│     "Return JSON with structure: {...}"     │
├─────────────────────────────────────────────┤
│  6. CONSTRAINTS & RULES                     │  ← What NOT to do
│     "Never..., Always..., Must..."          │
├─────────────────────────────────────────────┤
│  7. EXAMPLES (Optional)                     │  ← Few-shot examples
│     "Example input: ..., Output: ..."       │
└─────────────────────────────────────────────┘
```

---

## Prompt Engineering Principles

### 1. Be Specific and Explicit

❌ **Bad:**
```
Generate some interview questions for this job and candidate.
```

✅ **Good:**
```
Analyze the provided Job Description and Candidate CV. 
Generate exactly 10 interview questions that:
- Match the candidate's experience level (middle)
- Cover required skills from the JD
- Follow 60% technical, 20% behavioral, 20% situational distribution
- Include evaluation criteria for each question
```

### 2. Define Clear Output Format

❌ **Bad:**
```
Return the questions in a nice format.
```

✅ **Good:**
```json
Return a JSON object with this exact structure:
{
  "questions": [
    {
      "question_id": "Q1",
      "category": "technical" | "behavioral" | "situational",
      "difficulty": "junior" | "middle" | "senior",
      "question_text": "...",
      "key_points": ["...", "..."],
      "evaluation_criteria": ["...", "..."]
    }
  ]
}
```

### 3. Provide Context and Reasoning

❌ **Bad:**
```
Score the candidate's answer from 0-10.
```

✅ **Good:**
```
Evaluate the candidate's answer based on:
1. Technical Accuracy (0-10): How correct is the technical content?
2. Communication Clarity (0-10): How clearly did they explain?
3. Depth of Knowledge (0-10): How deep is their understanding?

For each dimension, provide:
- Numeric score
- Reasoning (2-3 sentences)
- Specific evidence from the answer
```

### 4. Use Role-Playing

Vai trò giúp model "think" theo perspective cụ thể:

```
You are a Senior Backend Engineer with 10 years of experience.
You've interviewed 100+ candidates and have high standards for:
- Code quality and best practices
- System design thinking
- Real-world problem-solving experience

Approach this evaluation with that mindset.
```

### 5. Chain of Thought

Hướng dẫn model "think step by step":

```
Follow this process:
1. First, read the entire conversation transcript
2. Identify key technical topics discussed
3. For each topic, note what the candidate said well and what they missed
4. Evaluate communication quality across all turns
5. Assess behavioral indicators (attitude, curiosity, teamwork)
6. Synthesize all observations into dimension scores
7. Generate final hiring recommendation with evidence
```

---

## Tuning Process

### Step 1: Baseline Testing

```bash
# Run agent with current prompt
python test_agent.py --input sample_data.json --output baseline_result.json

# Evaluate output quality
python evaluate_output.py baseline_result.json
```

### Step 2: Identify Issues

Common issues:
- ❌ Wrong output format (not valid JSON)
- ❌ Missing required fields
- ❌ Scores too lenient/harsh
- ❌ Generic responses without specifics
- ❌ Inconsistent quality across runs

### Step 3: Modify Prompt

```python
# Before
prompt = "Generate interview questions based on JD and CV."

# After - Adding specificity
prompt = """
You are QuestionCraft AI, an expert Interview Question Architect.

TASK: Generate {num_questions} interview questions tailored to:
- Position: {position}
- Level: {level}
- Key requirements from JD
- Candidate's actual experience from CV

RULES:
1. Questions must be scenario-based, not theoretical
2. Match difficulty to the stated level
3. Reference specific items from JD/CV when possible
4. Maintain 60-20-20 distribution (Technical-Behavioral-Situational)

OUTPUT: Return valid JSON only, no explanations.
"""
```

### Step 4: A/B Testing

```python
results = []
for prompt_version in ["v1", "v2", "v3"]:
    result = run_test_suite(prompt_version)
    results.append({
        "version": prompt_version,
        "quality_score": result.quality,
        "latency_ms": result.latency,
        "consistency": result.consistency
    })

# Compare and choose best version
best = max(results, key=lambda x: x["quality_score"])
```

### Step 5: Validate at Scale

```bash
# Run on larger test set
python batch_test.py --prompt-version v3 --test-set full --num-samples 100

# Check consistency
python analyze_consistency.py results_v3.json
```

---

## Agent-Specific Guidelines

### QuestionCraft AI (Question Generator)

**Goal**: Generate relevant, well-structured interview questions

**Key Tuning Areas**:

1. **Question Relevance**
```
# Add explicit JD-CV matching instruction
"For each question, identify:
- Which JD requirement it addresses
- Which CV experience it probes
- Why this question matters for the role"
```

2. **Difficulty Calibration**
```
# Define clear difficulty levels
"Junior: Basic syntax, concepts, tools usage
Middle: Design decisions, trade-offs, debugging
Senior: Architecture, scalability, leadership"
```

3. **Category Distribution**
```
# Enforce distribution strictly
"You MUST generate exactly:
- 6 Technical questions (60%)
- 2 Behavioral questions (20%)
- 2 Situational questions (20%)

If you generate 10 questions total, this means 6-2-2 split."
```

### DialogFlow AI (Conversation Agent)

**Goal**: Maintain natural conversation flow while evaluating

**Key Tuning Areas**:

1. **Tone and Warmth**
```
"Your communication style:
- Warm and encouraging, like a supportive mentor
- Professional but not cold
- Use positive language: 'Great point!', 'Interesting perspective...'
- Avoid judgmental phrases: 'That's wrong', 'You should know this'"
```

2. **Follow-up Logic**
```
"Decide next action based on:
- If answer is excellent (8-10): Acknowledge and move to next question
- If answer is good but shallow (5-7): Ask ONE follow-up for depth
- If answer is off-topic or poor (<5): Gently redirect and ask simpler version
- If 3+ follow-ups on same question: Move on regardless"
```

3. **Evaluation Consistency**
```
"Scoring guide:
9-10: Exceptional - Goes beyond expectations, provides insights
7-8: Strong - Correct, clear, with good examples
5-6: Adequate - Basic understanding, lacks depth
3-4: Weak - Partial understanding, some errors
0-2: Poor - Fundamentally incorrect or off-topic"
```

### EvalMaster AI (Performance Evaluator)

**Goal**: Generate comprehensive, evidence-based evaluation

**Key Tuning Areas**:

1. **Evidence Requirements**
```
"For EVERY score, you MUST provide:
- At least 2 specific quotes or examples from the transcript
- Turn numbers where evidence appears (e.g., 'Turn 3: candidate said...')
- Explanation of why this evidence supports the score"
```

2. **Dimension Weights**
```
"Calculate final score as weighted average:
- Technical Competency: 50% (most important)
- Communication Skills: 25%
- Behavioral Fit: 25%

Example: If scores are Technical=8, Communication=7, Behavioral=6
Final = (8×0.5) + (7×0.25) + (6×0.25) = 4.0 + 1.75 + 1.5 = 7.25"
```

3. **Hiring Recommendation Logic**
```
"Hiring decision thresholds:
- Strong Hire (8.0+): Clear hire, high confidence
- Hire (6.5-7.9): Hire with normal confidence
- Consider (5.0-6.4): Borderline, may need another interview
- No Hire (<5.0): Clear no

Consider these factors:
- Is final score above threshold?
- Any critical red flags? (dishonesty, poor attitude)
- Any exceptional strengths worth noting?
- Team fit and cultural alignment"
```

---

## Testing and Validation

### Regression Testing

```python
# Save baseline outputs
def save_baseline():
    for test_case in test_suite:
        result = agent.process(test_case.input)
        save_json(f"baselines/{test_case.id}.json", result)

# Compare after prompt change
def check_regression():
    for test_case in test_suite:
        baseline = load_json(f"baselines/{test_case.id}.json")
        current = agent.process(test_case.input)
        
        # Check key metrics
        assert current.format == baseline.format
        assert abs(current.score - baseline.score) < 0.5
        assert current.required_fields == baseline.required_fields
```

### Human Evaluation

```python
def human_eval_sample():
    """Generate outputs for human review"""
    samples = random.sample(test_cases, k=20)
    
    for sample in samples:
        output = agent.process(sample.input)
        
        print(f"\n{'='*60}")
        print(f"Test Case: {sample.id}")
        print(f"Input: {sample.input[:200]}...")
        print(f"Output: {output}")
        print(f"\nRate quality (1-5): ", end="")
        
        human_score = int(input())
        save_rating(sample.id, human_score)
```

### Consistency Check

```python
def check_consistency(num_runs=5):
    """Run same input multiple times, check variance"""
    results = []
    
    for _ in range(num_runs):
        result = agent.process(test_input)
        results.append(result.score)
    
    variance = np.var(results)
    print(f"Score variance: {variance:.2f}")
    
    # Target: variance < 0.5 for good consistency
    assert variance < 0.5, "Too much variance in outputs"
```

---

## Common Patterns

### Pattern 1: Few-Shot Examples

Thêm ví dụ vào prompt để guide behavior:

```
EXAMPLE INPUT:
JD: "Backend Developer với Python, FastAPI, PostgreSQL"
CV: "3 năm kinh nghiệm Django, MySQL"

EXAMPLE OUTPUT:
{
  "question_id": "Q1",
  "category": "technical",
  "question_text": "Bạn có kinh nghiệm với Django nhưng vị trí này dùng FastAPI. Bạn có thể so sánh Django và FastAPI về cách xử lý async requests không?",
  "reasoning": "This probes candidate's adaptability and understanding of the key difference between their experience (Django/WSGI) and job requirement (FastAPI/ASGI)"
}
```

### Pattern 2: Explicit Constraints

```
CONSTRAINTS:
- NEVER generate generic questions like "Tell me about yourself"
- NEVER score all dimensions the same (shows lack of discrimination)
- NEVER exceed 2000 tokens in output
- ALWAYS reference specific items from input data
- ALWAYS use Vietnamese for questions, English for technical terms
```

### Pattern 3: Iterative Refinement

```
PROCESS:
1. Draft initial questions
2. Self-critique: Are they specific enough? Do they match the level?
3. Refine questions based on critique
4. Final check: All constraints satisfied?
5. Output final version
```

---

## Troubleshooting

### Issue: Inconsistent Output Format

**Problem**: Sometimes returns JSON, sometimes plain text

**Solution**:
```
# Be extremely explicit
OUTPUT FORMAT: You MUST return ONLY valid JSON, nothing else.
No explanations before or after.
No markdown code blocks.
Just pure JSON starting with { and ending with }.

CORRECT: {"questions": [...]}
WRONG: Here are the questions: {"questions": [...]}
WRONG: ```json\n{"questions": [...]}\n```
```

### Issue: Scores Too Lenient

**Problem**: All scores are 7-10, no discrimination

**Solution**:
```
SCORING CALIBRATION:
- Average candidate should score 5-6
- Only truly exceptional answers deserve 9-10
- Don't be afraid to give 3-4 for weak answers
- Use full range 0-10, not just 6-10

BENCHMARK:
- 10: Textbook perfect + novel insights
- 8: Strong answer with examples
- 6: Correct but superficial
- 4: Partially correct, significant gaps
- 2: Mostly incorrect
```

### Issue: Generic Responses

**Problem**: Responses lack specificity

**Solution**:
```
BAD EXAMPLE:
"Candidate demonstrated good technical knowledge"

GOOD EXAMPLE:
"Candidate demonstrated strong async programming knowledge. In Turn 2, they correctly explained ASGI vs WSGI and provided specific performance metrics (800ms → 300ms) from their production experience."

RULE: Every observation must cite specific evidence with turn numbers or quotes.
```

### Issue: High Latency

**Problem**: Generation takes too long

**Solution**:
```python
# Reduce prompt length
# Remove verbose examples
# Use num_predict parameter

config = {
    "model_parameters": {
        "num_predict": 1024,  # Limit output tokens
        "temperature": 0.7,   # Lower = faster but less creative
        "top_k": 40,          # Reduce search space
    }
}
```

---

## Advanced Techniques

### Temperature Tuning

```python
# Temperature controls randomness
temperatures = {
    "question_generator": 0.7,   # Some creativity needed
    "conversation_agent": 0.8,   # Natural, varied responses
    "evaluator": 0.5             # Consistent, analytical
}
```

### Prompt Chaining

For complex tasks, break into multiple prompts:

```python
# Step 1: Analysis
analysis = agent.analyze(interview_transcript)

# Step 2: Scoring (uses analysis)
scores = agent.score(analysis_result=analysis)

# Step 3: Report (uses both)
report = agent.generate_report(
    analysis=analysis,
    scores=scores
)
```

### Dynamic Prompts

Adjust prompt based on context:

```python
def build_prompt(level: str):
    base_prompt = load_template("base_prompt.txt")
    
    if level == "senior":
        base_prompt += "\nFocus on architecture and leadership questions."
    elif level == "junior":
        base_prompt += "\nFocus on fundamentals and learning potential."
    
    return base_prompt
```

---

## Resources

- **Prompt Engineering Guide**: https://www.promptingguide.ai
- **OpenAI Best Practices**: https://platform.openai.com/docs/guides/prompt-engineering
- **Anthropic Prompt Library**: https://docs.anthropic.com/claude/prompt-library

---

## Appendix: Prompt Templates

See files:
- `prompts/question_generator_prompt.txt`
- `prompts/conversation_agent_prompt.txt`
- `prompts/performance_evaluator_prompt.txt`

For the complete, production-ready prompts.

---

For more information:
- [README.md](./README.md) - Project overview
- [INTEGRATION_GUIDE.md](./INTEGRATION_GUIDE.md) - Backend integration
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Testing procedures
