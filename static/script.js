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
const progressBar = document.getElementById('progress-bar'); // 追加

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
        
        updateAccuracyRate();
        updateProgressBar();
        
        quizQuestionNumber.textContent = `第${currentQuizIndex + 1}問 / ${totalQuizzes}問`;
        quizQuestion.innerHTML = quiz.question;
        
        quizButtons.innerHTML = '';
        const options = ['①', '②', '③', '④'];
        options.forEach(option => {
            const button = document.createElement('button');
            button.textContent = option;
            button.classList.add('quiz-button');
            button.addEventListener('click', () => checkAnswer(option, button));
            quizButtons.appendChild(button);
        });

        quizResult.classList.add('hidden');
    } else {
        finishQuiz();
    }
}

// 正答率を更新する関数
function updateAccuracyRate() {
    const answeredCount = currentQuizIndex;
    if (answeredCount > 0) {
        const accuracy = (correctAnswers / answeredCount) * 100;
        quizAccuracyRate.textContent = `正答率: ${accuracy.toFixed(1)}% (${correctAnswers}/${answeredCount}問)`;
    } else {
        quizAccuracyRate.textContent = `正答率: - % (0/0問)`;
    }
}

// プログレスバーを更新する関数
function updateProgressBar() {
    const progress = (currentQuizIndex / totalQuizzes) * 100;
    progressBar.style.width = `${progress}%`;
    progressBar.textContent = `${Math.floor(progress)}%`;
}


// 解答判定
function checkAnswer(userAnswer, clickedButton) {
    const currentQuiz = quizzes[currentQuizIndex];
    
    Array.from(quizButtons.children).forEach(button => {
        button.disabled = true;
        
        if (button.textContent === currentQuiz.answer) {
            button.classList.add('correct');
        } else if (button.textContent === userAnswer) {
            button.classList.add('incorrect');
        }
    });

    if (userAnswer === currentQuiz.answer) {
        correctAnswers++;
        quizCommentary.innerHTML = `正解！<br><br>${currentQuiz.commentary}`;
    } else {
        const commentary = currentQuiz.commentary.replace(new RegExp(`(正解は「${currentQuiz.answer}」です)`, 'g'), `<span class="correct-highlight">$1</span>`);
        quizCommentary.innerHTML = `残念！<br><br>${commentary}`;
        
        // 不正解の選択肢も強調
        const incorrectCommentary = quizCommentary.innerHTML.replace(new RegExp(`(残念！)`, 'g'), `<span class="incorrect-highlight">$1</span>`);
        quizCommentary.innerHTML = incorrectCommentary;
    }
    
    updateAccuracyRate();
    updateProgressBar();

    quizResult.classList.remove('hidden');
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
    accuracyRate.textContent = `正答率: ${accuracy.toFixed(1)}% (${correctAnswers}/${totalQuizzes}問)`;
    
    document.getElementById('quiz-container').classList.add('hidden');
    quizCompletion.classList.remove('hidden');

    sessionStorage.clear();
}