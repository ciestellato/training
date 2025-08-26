<%@ page language="java" contentType="text/html; charset=UTF-8"
    pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>ログインページ</title>
</head>
<body>

  <h2>ログイン</h2>
  <form action="LoginServlet" method="post">
    <label>ユーザID：</label><br>
    <input type="text" name="userId" required><br><br>

    <label>パスワード：admin を入力</label><br>
    <input type="password" name="password" required><br><br>

    <button type="submit">ログイン</button>
  </form>

</body>
</html>