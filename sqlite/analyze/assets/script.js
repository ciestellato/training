// ページ読み込み時にログを表示
document.addEventListener('DOMContentLoaded', function () {
    console.log("Dashアプリが読み込まれました 🚀");
});

// ログアウトボタンにホバー効果を追加
const logoutButton = document.getElementById('logout-button');
if (logoutButton) {
    logoutButton.addEventListener('mouseover', function () {
        logoutButton.style.opacity = '0.8';
    });
    logoutButton.addEventListener('mouseout', function () {
        logoutButton.style.opacity = '1';
    });
}

// 処理ログの自動スクロール
const logOutput = document.getElementById('log-output');
if (logOutput) {
    const observer = new MutationObserver(() => {
        logOutput.scrollTop = logOutput.scrollHeight;
    });
    observer.observe(logOutput, { childList: true });
}