<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
  <title>社員一覧</title>
  <style>
    table {
      border-collapse: collapse;
      width: 80%;
      margin: 20px auto;
    }
    th, td {
      border: 1px solid #999;
      padding: 8px 12px;
      text-align: center;
    }
    th {
      background-color: #f2f2f2;
    }
  </style>
  
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
	<li><a href="home.jsp">ホームに戻る</a></li>
</ul>

  <h2 style="text-align:center;">社員データ一覧</h2>
  <table>
    <thead>
      <tr>
        <th>社員ID</th>
        <th>社員名</th>
        <th>部署名</th>
        <th>ユーザID</th>
        <th>パスワード</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>1001</td>
        <td>田中 太郎</td>
        <td>営業部</td>
        <td>tanaka</td>
        <td>pass123</td>
      </tr>
      <tr>
        <td>1002</td>
        <td>佐藤 花子</td>
        <td>総務部</td>
        <td>sato</td>
        <td>hanako456</td>
      </tr>
      <tr>
        <td>1003</td>
        <td>鈴木 一郎</td>
        <td>開発部</td>
        <td>suzuki</td>
        <td>dev789</td>
      </tr>
      <tr>
        <td>1004</td>
        <td>山田 美咲</td>
        <td>人事部</td>
        <td>yamada</td>
        <td>misaki321</td>
      </tr>
      <tr>
        <td>1005</td>
        <td>高橋 健</td>
        <td>企画部</td>
        <td>takahashi</td>
        <td>plan654</td>
      </tr>
    </tbody>
  </table>
</body>
</html>
