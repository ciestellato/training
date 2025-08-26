package servlet;

import java.io.IOException;

import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class LoginServlet
 */
@WebServlet("/LoginServlet")
public class LoginServlet extends HttpServlet {
	
	private static final long serialVersionUID = 1L;

	protected void doPost(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {
		// ユーザIDとパスワードを取得
		String userId = request.getParameter("userId");
		String password = request.getParameter("password");

		// 簡易的な認証（実際はDBなどでチェック）
		// パスワードが、admin ならばログイン後の画面へ遷移
		if ("admin".equals(password)) {
			// ユーザIDをリクエスト属性に追加
			request.setAttribute("userId", userId);
			
			
			// ●複数のリクエストをまたいで共有したいデータはセッションデータを使う
			// セッションを取得（存在しない場合は新規作成）
//		    HttpSession session = request.getSession();
//		    // セッションにユーザIDを保存
//		    session.setAttribute("userId", userId);


			// home.jsp にフォワード
			RequestDispatcher dispatcher = request.getRequestDispatcher("home.jsp");
			dispatcher.forward(request, response);
		} else {
			// 認証失敗時はログインページに戻す
			// エラーメッセージをリクエスト属性に追加
			request.setAttribute("errorMsg", "ユーザIDまたはパスワードが違います。");
			RequestDispatcher dispatcher = request.getRequestDispatcher("error.jsp");
			dispatcher.forward(request, response);
		}

	}

}
