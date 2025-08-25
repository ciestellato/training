package dbServlet;

import java.io.IOException;
import java.io.PrintWriter;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import jakarta.servlet.http.HttpSession;

//このServletは /session にアクセスされたときに動作します
@WebServlet("/session")
public class SessionServlet extends HttpServlet {

	@Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response)
			throws ServletException, IOException {

		// 日本語の文字化けを防ぐための設定
		response.setContentType("text/html; charset=UTF-8");

		// セッションを取得（なければ新しく作る）
		HttpSession session = request.getSession();

		// 個人のアクセス回数を保持する変数を宣言
		int count;

		// セッションが新規（初回アクセス）の場合
		if (session.isNew()) {
			// 初回なのでカウントを1に設定
			count = 1;

			// セッションに "count" という名前で保存
			session.setAttribute("count", count);
		} else {
			// すでにセッションが存在する場合は、保存されている "count" を取得
			count = (int) session.getAttribute("count");

			// アクセス回数を1増やす
			count++;

			// 更新されたカウントを再度セッションに保存
			session.setAttribute("count", count);
		}

		// 出力用の準備
		PrintWriter out = response.getWriter();

		// HTMLで表示
		out.println(count + "回目のアクセスです。<hr>");
		out.println("<h3>複数回のアクセスでリクエストとレスポンスは毎回新規生成されるが、セッションは同じものが流用される</h3>");
		out.println("request番号：" + request.hashCode() + "<br>");// hashCode()はメモリ上の管理番号を取得する
		out.println("response番号：" + response.hashCode() + "<br>");
		out.println("session番号：" + session.getId());
		out.println("<hr>");
		out.println("<a href='session'>SessionServletを再呼び出し</a>");
	}

	/*
	 * Edgeでクッキーを確認する手順
	✅ 方法①：開発者ツール（F12）を使う
	1. 	Edgeで対象のWebページを開く
	2. 	キーボードで  を押す（または右クリック →「検証」）
	3. 	上部メニューから「Application（アプリケーション）」タブを選択
	4. 	左側メニューの「Cookies」を展開し、対象のドメインをクリック
	5. 	右側にクッキーの一覧が表示される
	• 	：クッキー名
	• 	：保存されている値
	 */

}
