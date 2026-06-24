let currentModule = null;
let currentQuestion = 1;

function initializeModule(moduleConfig) {
    currentModule = moduleConfig;
    currentQuestion = 1;

    // Check if already completed
    const lastAnsweredQuestion = Math.max(
        ...Object.keys(moduleConfig.userAnswers).map(Number)
    );

    if (lastAnsweredQuestion > 0 && lastAnsweredQuestion <= moduleConfig.totalQuestions) {
        currentQuestion = lastAnsweredQuestion + 1;
    }

    // Load and display the current question
    displayQuestion(currentQuestion);
}

function displayQuestion(questionNumber) {
    if (!currentModule) return;

    const container = document.getElementById('socratic-container');
    const completionMsg = document.getElementById('completion-message');
    const reviewSection = document.getElementById('review-section');

    // Check if all questions are answered
    if (questionNumber > currentModule.totalQuestions) {
        container.style.display = 'none';
        completionMsg.style.display = 'block';
        reviewSection.style.display = 'none';
        return;
    }

    completionMsg.style.display = 'none';
    reviewSection.style.display = 'none';
    container.style.display = 'block';

    // Fetch the question
    fetch(`/api/module/${currentModule.moduleDate}/questions`)
        .then(response => response.json())
        .then(data => {
            const question = data.questions.find(q => q.question_number === questionNumber);
            if (question) {
                renderQuestion(question, questionNumber, data.questions.length);
            }
        })
        .catch(error => console.error('Error loading questions:', error));
}

function renderQuestion(question, questionNumber, totalQuestions) {
    const container = document.getElementById('socratic-container');
    const progressText = document.getElementById('progress-text');

    progressText.textContent = `Question ${questionNumber} of ${totalQuestions}`;

    // Check if this question was already answered
    const hasAnswer = currentModule.userAnswers && currentModule.userAnswers[String(questionNumber)];

    if (hasAnswer) {
        // Show answered state with model answer
        renderAnsweredQuestion(question, questionNumber, totalQuestions);
    } else {
        // Show unanswered question
        renderUnansweredQuestion(question, questionNumber, totalQuestions);
    }
}

function renderUnansweredQuestion(question, questionNumber, totalQuestions) {
    const container = document.getElementById('socratic-container');

    container.innerHTML = `
        <div class="question-box">
            <h4>Question ${questionNumber}/${totalQuestions}</h4>
            <p>${question.question_text}</p>

            <textarea
                id="answer-input"
                class="answer-input"
                placeholder="Type your answer here... (Think deeply and provide a thoughtful response)"
            ></textarea>

            <button class="submit-btn" onclick="submitAnswer(${questionNumber})">
                Submit Answer
            </button>
        </div>
    `;

    // Focus on the textarea
    setTimeout(() => {
        document.getElementById('answer-input').focus();
    }, 100);
}

function renderAnsweredQuestion(question, questionNumber, totalQuestions) {
    const container = document.getElementById('socratic-container');
    const userAnswer = currentModule.userAnswers[String(questionNumber)] || '';

    container.innerHTML = `
        <div class="question-box">
            <h4>Question ${questionNumber}/${totalQuestions}</h4>
            <p>${question.question_text}</p>

            <div style="margin-bottom: 1.5rem; padding: 1rem; background-color: #f0f0f0; border-radius: 4px;">
                <strong>Your Answer:</strong>
                <p style="margin-top: 0.5rem; font-style: italic;">${userAnswer}</p>
            </div>

            <div class="model-answer-box">
                <h5>✓ Model Answer</h5>
                <p>${question.model_answer || 'No model answer provided.'}</p>
            </div>

            <div class="explanation-box">
                <h5>💡 Why This Matters</h5>
                <p>${question.explanation || 'No explanation provided.'}</p>
            </div>

            <button class="next-btn" onclick="displayQuestion(${questionNumber + 1})">
                ${questionNumber === totalQuestions ? 'Complete Module' : 'Next Question'} →
            </button>
        </div>
    `;
}

function submitAnswer(questionNumber) {
    const answerInput = document.getElementById('answer-input');
    const userAnswer = answerInput.value.trim();

    if (!userAnswer) {
        alert('Please provide an answer before submitting.');
        return;
    }

    // Disable submit button to prevent double submission
    const submitBtn = document.querySelector('.submit-btn');
    submitBtn.disabled = true;
    submitBtn.textContent = 'Submitting...';

    // Send answer to backend
    fetch('/api/socratic/submit', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            module_date: currentModule.moduleDate,
            question_number: questionNumber,
            user_answer: userAnswer,
        }),
    })
        .then(response => response.json())
        .then(data => {
            // Update local user answers
            currentModule.userAnswers[String(questionNumber)] = userAnswer;

            // Display the answered version
            displayQuestion(questionNumber);
        })
        .catch(error => {
            console.error('Error submitting answer:', error);
            alert('Error saving your answer. Please try again.');
            submitBtn.disabled = false;
            submitBtn.textContent = 'Submit Answer';
        });
}

function showReview() {
    const container = document.getElementById('socratic-container');
    const completionMsg = document.getElementById('completion-message');
    const reviewSection = document.getElementById('review-section');

    if (!currentModule) return;

    container.style.display = 'none';
    completionMsg.style.display = 'none';
    reviewSection.style.display = 'block';

    fetch(`/api/module/${currentModule.moduleDate}/review`)
        .then(response => response.json())
        .then(data => {
            const reviewContent = document.getElementById('review-content');
            let html = '<div class="review-questions">';

            data.questions.forEach((q, index) => {
                html += `
                    <div class="review-question" style="margin-bottom: 2rem; padding: 1rem; border: 1px solid #ddd; border-radius: 4px;">
                        <h4>Question ${index + 1}: ${q.question_text}</h4>

                        <div style="margin: 1rem 0; padding: 1rem; background-color: #f0f0f0; border-radius: 4px;">
                            <strong>Your Answer:</strong>
                            <p style="margin-top: 0.5rem; font-style: italic;">${q.user_answer || '(Not answered)'}</p>
                        </div>

                        <div style="margin: 1rem 0; padding: 1rem; background-color: #d5f4e6; border-left: 4px solid #27ae60; border-radius: 4px;">
                            <strong style="color: #27ae60;">Model Answer:</strong>
                            <p style="margin-top: 0.5rem;">${q.model_answer}</p>
                        </div>

                        <div style="margin: 1rem 0; padding: 1rem; background-color: #fff3cd; border-left: 4px solid #ffc107; border-radius: 4px;">
                            <strong style="color: #856404;">Explanation:</strong>
                            <p style="margin-top: 0.5rem;">${q.explanation}</p>
                        </div>
                    </div>
                `;
            });

            html += '</div>';
            reviewContent.innerHTML = html;
        })
        .catch(error => {
            console.error('Error loading review:', error);
            const reviewContent = document.getElementById('review-content');
            reviewContent.innerHTML = '<p>Error loading review. Please try again.</p>';
        });
}

function goBackToModule() {
    const container = document.getElementById('socratic-container');
    const completionMsg = document.getElementById('completion-message');
    const reviewSection = document.getElementById('review-section');

    container.style.display = 'block';
    completionMsg.style.display = 'block';
    reviewSection.style.display = 'none';
}
