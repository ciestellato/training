package employeesSample;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class SimpleConnect1 {
	public static void main(String[] args) throws SQLException, ClassNotFoundException {
		
		// JDBCドライバーのロード（JDK 6以降は省略可能だが、明示しておくと安心）
		Class.forName("org.h2.Driver");


		// try-with-resourcesで接続を管理（自動でcloseされる）
		// データベースに接続
		Connection conn = DriverManager.getConnection(
				"jdbc:h2:tcp://localhost/~/example", // H2のTCPモードでexample DBに接続
				"sa", // ユーザー名（H2のデフォルト）
				"" // パスワード（空文字がデフォルト）
		);
		
		// ここではテーブル操作などは行わず、接続確認のみ
		System.out.println("データベースに接続しました");
			
		// データベース接続を終了
		conn.close();
	}
}