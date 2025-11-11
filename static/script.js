// script.js

// グローバル変数
let quizzes = [];
let currentQuizIndex = 0;
let correctAnswers = 0;
let totalQuizzes = 0;

// DOM要素
const startButton = document.getElementById('start-button');
const yearSelect = document.getElementById('year-select');
const genreSelect = document.getElementById('genre-select');
const quizQuestionNumber = document.getElementById('quiz-question-number');
const quizQuestion = document.getElementById('quiz-question');
const quizButtons = document.getElementById('quiz-buttons');
const quizResult = document.getElementById('quiz-result');
const quizCommentary = document.getElementById('quiz-commentary');
const nextButton = document.getElementById('next-button');
const endButton = document.getElementById('end-button');
const quizCompletion = document.getElementById('quiz-completion');
const accuracyRate = document.getElementById('accuracy-rate');
const backToHomeButton = document.getElementById('back-to-home-button');
const quizAccuracyRate = document.getElementById('quiz-accuracy-rate');
const progressBar = document.getElementById('progress-bar');

// イベントリスナー
if (startButton) {
    startButton.addEventListener('click', startQuiz);
}
if (nextButton) {
    nextButton.addEventListener('click', nextQuiz);
}
if (endButton) {
    endButton.addEventListener('click', finishQuiz);
}
if (backToHomeButton) {
    backToHomeButton.addEventListener('click', () => {
        window.location.href = '/';
    });
}

// クイズ開始処理
async function startQuiz() {
    const year = yearSelect.value;
    const genre = genreSelect.value;
    
    try {
        const response = await fetch('/api/quiz', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ year: year, genre: genre })
        });

        const data = await response.json();

        if (response.ok) {
            quizzes = data;
            if (quizzes.length === 0) {
                alert('選択した条件の問題が見つかりませんでした。');
                return;
            }
            totalQuizzes = quizzes.length;
            currentQuizIndex = 0;
            correctAnswers = 0;

            sessionStorage.setItem('quizzes', JSON.stringify(quizzes));
            sessionStorage.setItem('currentQuizIndex', currentQuizIndex);
            sessionStorage.setItem('correctAnswers', correctAnswers);

            window.location.href = `/quiz?year=${year}&genre=${genre}`;
        } else {
            alert(data.error);
        }
    } catch (error) {
        console.error('API呼び出しエラー:', error);
        alert('問題データの取得に失敗しました。');
    }
}

// クイズページでの初期化
if (window.location.pathname === '/quiz') {
    window.onload = () => {
        quizzes = JSON.parse(sessionStorage.getItem('quizzes'));
        currentQuizIndex = parseInt(sessionStorage.getItem('currentQuizIndex'));
        correctAnswers = parseInt(sessionStorage.getItem('correctAnswers'));
        totalQuizzes = quizzes.length;
        displayQuiz();
    };
}

// 問題の表示
function displayQuiz() {
    if (currentQuizIndex < totalQuizzes) {
        const quiz = quizzes[currentQuizIndex];

        // Update accuracy rate and progress bar
        updateAccuracyRate();
        updateProgressBar(currentQuizIndex, totalQuizzes);

        // Display question number and year
        quizQuestionNumber.textContent = `第${currentQuizIndex + 1}問 / ${totalQuizzes}問 (${quiz.year})`;
        quizQuestion.innerHTML = quiz.question;

        quizButtons.innerHTML = '';
        const options = ['①', '②', '③', '④'];
        options.forEach(option => {
            const button = document.createElement('button');
            button.textContent = option;
            button.classList.add('quiz-button');
            // Pass the button itself on click
            button.addEventListener('click', () => checkAnswer(option, button));
            quizButtons.appendChild(button);
        });

        quizResult.classList.add('hidden');
        quizResult.classList.remove('correct-box', 'incorrect-box'); // Reset previous result styles
    } else {
        finishQuiz();
    }
}

// 正答率を更新する関数
function updateAccuracyRate() {
    // Exclude the current question from the accuracy calculation
    const answeredCount = currentQuizIndex; // Only count answered questions
    if (answeredCount > 0) {
        const accuracy = (correctAnswers / answeredCount) * 100;
        quizAccuracyRate.textContent = `正答率: ${accuracy.toFixed(1)}% (${correctAnswers}/${answeredCount}問)`;
    } else {
        quizAccuracyRate.textContent = `正答率: - % (0/0問)`;
    }
}

// プログレスバーを更新する関数
function updateProgressBar(currentIndex, totalCount) {
    // 表示する進捗は「回答済み数 / totalCount」ベースにする
    const answeredCount = currentIndex + (quizResult && !quizResult.classList.contains('hidden') ? 1 : 0);
    const progress = (answeredCount / totalCount) * 100;
    progressBar.style.width = `${progress}%`;
    progressBar.textContent = `${Math.floor(progress)}%`;
}


// 解答判定
function checkAnswer(selectedOption, button) {
    const quiz = quizzes[currentQuizIndex];
    const correctOption = quiz.answer;

    // Highlight the selected option
    const buttons = document.querySelectorAll('.quiz-button');
    buttons.forEach(btn => {
        if (btn.textContent === correctOption) {
            btn.classList.add('correct-answer'); // Highlight correct answer
        } else if (btn === button) {
            btn.classList.add('selected-answer'); // Highlight selected answer
        } else {
            btn.classList.add('incorrect-answer'); // Highlight incorrect answers
        }
        btn.disabled = true; // Disable all buttons after selection
    });

    // Show explanation
    quizResult.textContent = quiz.commentary;
    quizResult.classList.remove('hidden');
    quizResult.classList.add('explanation-box');

    if (selectedOption === correctOption) {
        correctAnswers++;
        quizResult.classList.add('correct-box');
    } else {
        quizResult.classList.add('incorrect-box');
    }

    currentQuizIndex++;
    setTimeout(displayQuiz, 2000); // Move to the next question after 2 seconds
}

// 次の問題へ
function nextQuiz() {
    currentQuizIndex++;
    sessionStorage.setItem('currentQuizIndex', currentQuizIndex);
    sessionStorage.setItem('correctAnswers', correctAnswers);
    displayQuiz();
}

// クイズ終了
function finishQuiz() {
    const accuracy = (correctAnswers / totalQuizzes) * 100;
    quizContainer.innerHTML = ''; // Clear the quiz container

    const resultMessage = document.createElement('div');
    resultMessage.classList.add('result-message');

    if (accuracy === 100) {
        resultMessage.innerHTML = `<h2>🎉 完璧です！正答率: ${accuracy.toFixed(1)}%</h2>`;
    } else if (accuracy >= 80) {
        resultMessage.innerHTML = `<h2>✨ 素晴らしい！正答率: ${accuracy.toFixed(1)}%</h2>`;
    } else if (accuracy >= 50) {
        resultMessage.innerHTML = `<h2>👍 よく頑張りました！正答率: ${accuracy.toFixed(1)}%</h2>`;
    } else {
        resultMessage.innerHTML = `<h2>😅 次回はもっと頑張りましょう！正答率: ${accuracy.toFixed(1)}%</h2>`;
    }

    quizContainer.appendChild(resultMessage);
}