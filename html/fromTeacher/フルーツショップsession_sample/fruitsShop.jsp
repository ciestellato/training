<%@ page language="java" contentType="text/html; charset=UTF-8"
	pageEncoding="UTF-8"%>
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>Insert title here</title>
</head>
<body>
<h3>フルーツショップ</h3>
<hr>

	<form action="FruitShopServlet" method="post">
			<label for="fruit">購入する果物を選んでください：</label><br> 
			 <select name="fruit"
				id="fruit" required>
				<option value="">-- 選択してください --</option>
				<option value="りんご">りんご</option>
				<option value="みかん">みかん</option>
				<option value="バナナ">バナナ</option>
				<option value="メロン">メロン</option>
			</select>
			<br> 
			<label for="quantity">購入個数を選んでください（1〜10個）：</label><br>  
			<select name="quantity" id="quantity" required>
				<option value="">-- 選択してください --</option>
				<!-- 数値をループで生成する場合はJavaScriptでも可能ですが、ここでは手動で記述 -->
				<option value="1">1個</option>
				<option value="2">2個</option>
				<option value="3">3個</option>
				<option value="4">4個</option>
				<option value="5">5個</option>
			</select> <br><br> 

		<input type="submit" value="購入">
	</form>


</body>
</html>