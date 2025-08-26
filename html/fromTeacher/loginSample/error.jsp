<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Insert title here</title>
</head>
<body>

<%
// リクエストからエラーメッセージ属性データを取得
String errorMsg = (String) request.getAttribute("errorMsg");
%>

<p>
	<font style="color: red"> 
		<%=errorMsg%>
	</font>
</p>
	
	<a href="login.jsp">ログインページ</a>

</body>
</html>