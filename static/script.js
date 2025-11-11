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
function checkAnswer(userAnswer, clickedButton) {
    const currentQuiz = quizzes[currentQuizIndex];
    let isCorrect = (userAnswer === currentQuiz.answer);

    // 全てのボタンを無効化し、色を変更
    Array.from(quizButtons.children).forEach(button => {
        button.disabled = true;
        
        if (button.textContent === currentQuiz.answer) {
            // 正解ボタンを緑色に
            button.classList.add('correct');
        } else if (button.textContent === userAnswer) {
            // 不正解のボタンを赤色に
            button.classList.add('incorrect');
        }
    });

    // 正答率の更新
    if (isCorrect) {
        correctAnswers++;
        quizResult.classList.add('correct-box');
        quizCommentary.innerHTML = `<span class="correct-highlight">正解！</span><br><br>${currentQuiz.commentary}`;
    } else {
        quizResult.classList.add('incorrect-box');
        
        // 解説文を強調表示
        let commentaryHTML = currentQuiz.commentary;
        
        // 1. 正解の選択肢を強調
        commentaryHTML = commentaryHTML.replace(new RegExp(`(${currentQuiz.answer}:)`, 'g'), `<span class="correct-highlight">$1</span>`);
        
        // 2. 不正解（ユーザーが選んだ選択肢）を強調
        commentaryHTML = commentaryHTML.replace(new RegExp(`(${userAnswer}:)`, 'g'), `<span class="incorrect-highlight">$1</span>`);

        quizCommentary.innerHTML = `<span class="incorrect-highlight">残念！</span> 正解は${currentQuiz.answer}です。<br><br>${commentaryHTML}`;
    }
    
    // updateAccuracyRate() は checkAnswer の先頭で呼び出されているため、ここでは不要。
    // ※ただし、正解数を反映させるため、finishQuiz関数や updateAccuracyRate 関数を調整しています。
    updateAccuracyRate(); 
    
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
    quizContainer.classList.add('hidden');
    quizResult.classList.remove('hidden');

    // Display a message based on the accuracy rate
    let message = '';
    if (accuracy === 100) {
        message = '🎉 完璧です！全問正解しました！🎉';
    } else if (accuracy >= 80) {
        message = '✨ 素晴らしい！高得点です！✨';
    } else if (accuracy >= 50) {
        message = '😊 よく頑張りました！次はもっと高得点を目指しましょう！';
    } else {
        message = '😅 もう少し頑張りましょう！次回に期待！';
    }

    quizResult.innerHTML = `
        <h2>クイズ終了</h2>
        <p>正答率: ${accuracy.toFixed(1)}% (${correctAnswers}/${totalQuizzes}問)</p>
        <p>${message}</p>
    `;

    // Clear session storage to reset the quiz state
    sessionStorage.clear();

    // Ensure the end button redirects to the home page
    backToHomeButton.addEventListener('click', () => {
        window.location.href = '/';
    });
}