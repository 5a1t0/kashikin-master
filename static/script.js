// script.js

// グローバル変数
let quizzes = []; // 取得した問題データを格納
let currentQuizIndex = 0; // 現在の問題番号
let correctAnswers = 0; // 正解数
let totalQuizzes = 0; // 全問題数

// DOM要素
const startButton = document.getElementById('start-button');
const yearSelect = document.getElementById('year-select');
const genreSelect = document.getElementById('genre-select');
const quizQuestionNumber = document.getElementById('quiz-question-number');
const quizQuestion = document.getElementById('quiz-question');
const correctButton = document.getElementById('correct-button');
const incorrectButton = document.getElementById('incorrect-button');
const quizButtons = document.getElementById('quiz-buttons');
const quizResult = document.getElementById('quiz-result');
const quizCommentary = document.getElementById('quiz-commentary');
const nextButton = document.getElementById('next-button');
const quizCompletion = document.getElementById('quiz-completion');
const accuracyRate = document.getElementById('accuracy-rate');
const backToHomeButton = document.getElementById('back-to-home-button');

// イベントリスナー
if (startButton) {
    startButton.addEventListener('click', startQuiz);
}
if (correctButton) {
    correctButton.addEventListener('click', () => checkAnswer('〇'));
}
if (incorrectButton) {
    incorrectButton.addEventListener('click', () => checkAnswer('×'));
}
if (nextButton) {
    nextButton.addEventListener('click', nextQuiz);
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
    
    // APIを呼び出して問題データを取得
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

            // クイズページへリダイレクト
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
    window.onload = async () => {
        const urlParams = new URLSearchParams(window.location.search);
        const year = urlParams.get('year');
        const genre = urlParams.get('genre');
        
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
                    alert('選択した条件の問題が見つかりませんでした。トップページに戻ります。');
                    window.location.href = '/';
                    return;
                }
                totalQuizzes = quizzes.length;
                currentQuizIndex = 0;
                correctAnswers = 0;
                displayQuiz();
            } else {
                alert(data.error);
                window.location.href = '/';
            }
        } catch (error) {
            console.error('API呼び出しエラー:', error);
            alert('問題データの取得に失敗しました。トップページに戻ります。');
            window.location.href = '/';
        }
    };
}

// 問題の表示
function displayQuiz() {
    if (currentQuizIndex < totalQuizzes) {
        const quiz = quizzes[currentQuizIndex];
        quizQuestionNumber.textContent = `第${currentQuizIndex + 1}問 / ${totalQuizzes}問`;
        quizQuestion.textContent = quiz.question;
        
        quizButtons.classList.remove('hidden');
        quizResult.classList.add('hidden');
    } else {
        // クイズ終了
        finishQuiz();
    }
}

// 解答判定
function checkAnswer(userAnswer) {
    const currentQuiz = quizzes[currentQuizIndex];
    
    if (userAnswer === currentQuiz.answer) {
        correctAnswers++;
        quizCommentary.innerHTML = `正解！<br><br>${currentQuiz.commentary}`;
    } else {
        quizCommentary.innerHTML = `残念！正解は「${currentQuiz.answer}」です。<br><br>${currentQuiz.commentary}`;
    }

    quizButtons.classList.add('hidden');
    quizResult.classList.remove('hidden');
}

// 次の問題へ
function nextQuiz() {
    currentQuizIndex++;
    displayQuiz();
}

// クイズ終了
function finishQuiz() {
    const accuracy = (correctAnswers / totalQuizzes) * 100;
    accuracyRate.textContent = `正答率: ${accuracy.toFixed(1)}% (${correctAnswers}/${totalQuizzes}問)`;
    
    document.getElementById('quiz-container').classList.add('hidden');
    quizCompletion.classList.remove('hidden');
}