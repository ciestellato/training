package servlet;

import java.io.IOException;
import java.io.PrintWriter;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;

/**
 * Servlet implementation class FruitShopServlet
 */
@WebServlet("/FruitShopServlet")
public class FruitShopServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;

	protected void doPost(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {

		//送信データの取得
		request.setCharacterEncoding("UTF-8");

		String fruit = request.getParameter("fruit");
		String quantity = request.getParameter("quantity");
		// 送信されたデータを文字列にしてつなぐ
		String inputData = fruit + ":" + quantity + "個<br>";

		// ●入力フォームのデータを蓄積したい！requestだと次ページを表示するとメモリから消えてしまう！
		// リクエストデータにひもづいたセッションデータを取得
		HttpSession session = request.getSession();
		// セッションデータに保持された文字列データ
		StringBuilder data = (StringBuilder) session.getAttribute("cartInfo");
		if (data == null) {
			// 1回目の呼び出し時はセッションに属性セットされていないので、新規にセットする
			data = new StringBuilder();
			session.setAttribute("cartInfo", data);
		}
		// 文字列データに、送信値を末尾に追加
		data.append(inputData);

		response.setContentType("text/html; charset=UTF-8");
		// ブラウザの画面に書き込みをするオブジェクトを取り出す
		PrintWriter out = response.getWriter();
		out.print("商品：" + fruit);
		out.print("<br>");
		out.print("個数：" + quantity);
		out.print("<br>");
		out.print("<a href=fruitsShop.jsp>戻る</a><hr>");
		// データを表示
		out.print("＊カートの中身＊<br>");
		out.print(data);
		out.print("<a href=BuyServlet>[購入する]</a><hr>");

	}

}
