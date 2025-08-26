<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ホーム</title>
</head>
<body>

<%  
	// リクエストデータから取得。後で、session..getAttribute("userId");に変更
	String userId = (String)request.getAttribute("userId");
%>

<%-- ログインしたユーザIDを表示する --%>
<p style="text-align: right;">ユーザID：<u><%=userId %></u></p>

<!-- リンクメニュー -->
<ul style="list-style-type: none;">
	<li><a href="login.jsp">ログアウト</a></li>
	<li><a href="userKanri.jsp">システムユーザ管理ページ</a></li>
	<li><a href="messageForm.jsp">一般ユーザへのメッセージフォームページ</a></li>
</ul>

<h2>ようこそ、管理者ホームページへ！</h2>

<p>
このページはシステム管理者用のページです。<br>
ユーザ管理や一般ユーザへのシステム使用上のメッセージを送信することができます。
</p>


</body>
</html>