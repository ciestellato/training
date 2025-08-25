package dbServlet;

import java.io.IOException;

import jakarta.servlet.RequestDispatcher;
import jakarta.servlet.ServletException;
import jakarta.servlet.annotation.WebServlet;
import jakarta.servlet.http.HttpServlet;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

/**
 * Servlet implementation class DBServletPost
 */
@WebServlet("/DBServletPost")
public class DBServletPost extends HttpServlet {

    // POSTリクエストを受け取ったときの処理
    @Override
    protected void doPost(HttpServletRequest request, HttpServletResponse response)
            throws ServletException, IOException {

        // 日本語の文字化けを防ぐために、文字コードをUTF-8に設定
        request.setCharacterEncoding("UTF-8");

        // フォームなどから送られてきたパラメータを取得
        String data = request.getParameter("data");
        
		// 以下にJDBCプログラムを挿入
        
        

        // JSPに渡すために、"data" という名前でリクエストにセット
        request.setAttribute("data", data);

        // result.jsp に処理を渡して、画面表示を任せる
        RequestDispatcher dispatcher = request.getRequestDispatcher("result.jsp");
        dispatcher.forward(request, response);
    }
}
