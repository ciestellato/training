package employeesSample;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.SQLException;

public class SimpleConnect3 {
	public static void main(String[] args) {

		// try-with-resourcesで接続を管理（自動でcloseされる）
		try (Connection conn = DriverManager.getConnection("jdbc:h2:tcp://localhost/~/example","sa","")) {

			System.out.println("データベースに接続しました");
			// ここではテーブル操作などは行わず、接続確認のみ

		} catch (SQLException e) {
			// 接続失敗や切断時の例外を処理
			System.out.println("データベース接続エラー: " + e.getMessage());
		}
	}
}