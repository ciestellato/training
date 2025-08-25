package dbServlet;

import java.io.IOException;
import java.io.PrintWriter;

import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;


// このServletは /DBAccessServlet にアクセスされたときに動作します
@WebServlet("/DBAServletGet")
public class DBAServletGet extends HttpServlet {

    // GETリクエストを受け取ったときの処理
    @Override
	protected void doGet(HttpServletRequest request, HttpServletResponse response) throws ServletException, IOException {

        // リクエスト、レスポンスに文字コードをUTF-8に設定（日本語対応のため）
        request.setCharacterEncoding("UTF-8");
        response.setContentType("text/html; charset=UTF-8");
        // 出力用のPrintWriterを取得
        PrintWriter out = response.getWriter();

        // リクエストパラメータ "name" を取得（例：?name=満さん）
        //String name = request.getParameter("name");

		// 以下にJDBCプログラムを挿入
        



        // HTMLとして画面に出力
        out.println();

    }
}