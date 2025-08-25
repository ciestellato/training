package servlet;

import java.io.IOException;
import java.io.PrintWriter;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;


@WebServlet("/BuyServlet")
public class BuyServlet extends HttpServlet {
	private static final long serialVersionUID = 1L;

	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {
		// セッションデータを取得
		HttpSession session = request.getSession();
		// セッションデータに保持された文字列データ(カート情報)を削除する
		session.removeAttribute("cartInfo");
		
		response.setContentType("text/html; charset=UTF-8");
		// ブラウザの画面に書き込みをするオブジェクトを取り出す
		PrintWriter out = response.getWriter();
		out.print("購入処理が完了しました。カートは空になりました。");
		out.print("<a href=fruitsShop.jsp>戻る</a><hr>");
	}

}
