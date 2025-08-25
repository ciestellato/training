package employeesSample;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class SimpleConnect2 {
	public static void main(String[] args) {
		
		// JDBCドライバーのロード（JDK 6以降は省略可能だが、明示しておくと安心）
		try {
			Class.forName("org.h2.Driver");
		} catch (ClassNotFoundException e) {
			System.out.println("JDBCドライバーが見つかりません: " + e.getMessage());
			return; // ドライバーがなければ接続できないので終了
		}

		// try-with-resourcesで接続を管理（自動でcloseされる）
		try (Connection conn = DriverManager.getConnection(
				"jdbc:h2:tcp://localhost/~/example", // H2のTCPモードでexample DBに接続
				"sa", // ユーザー名（H2のデフォルト）
				"" // パスワード（空文字がデフォルト）
		)) {
			
			System.out.println("データベースに接続しました");
			// ここではテーブル操作などは行わず、接続確認のみ

		} catch (SQLException e) {
			// 接続失敗や切断時の例外を処理
			System.out.println("データベース接続エラー: " + e.getMessage());
		}
	}
}