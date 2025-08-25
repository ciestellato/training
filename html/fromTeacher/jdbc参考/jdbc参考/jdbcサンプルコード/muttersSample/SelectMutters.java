package muttersSample;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;

public class SelectMutters {
	public static void main(String[] args) {

		// JDBCドライバーのロード（JDK 6以降は省略可能だが、明示しておくと安心）
		try {
			Class.forName("org.h2.Driver");
		} catch (ClassNotFoundException e) {
			System.out.println("JDBCドライバーが見つかりません: " + e.getMessage());
			return; // ドライバーがなければ接続できないので終了
		}

		// dokoTsubuデータベースに接続
		try (Connection conn = DriverManager.getConnection("jdbc:h2:tcp://localhost/~/dokoTsubu", "sa", "")) {

			// ●ここを修正：SELECT文を準備
			String sql = "SELECT 列名 FROM テーブル名";
			PreparedStatement pStmt = conn.prepareStatement(sql);

			// SELECT文を実行し、結果表（ResultSet）を取得
			ResultSet rs = pStmt.executeQuery();

			// 結果表に格納されたレコードの内容を表示
			while (rs.next()) {
				// ●ここを修正
				String id = rs.getString("ID");
				String name = rs.getString("NAME");
				int age = rs.getInt("AGE");

				// 取得したデータを出力
				System.out.println("ID:" + id);
				System.out.println("名前:" + name);
				System.out.println("年齢:" + age + "\n");
			}
		} catch (SQLException e) {
			e.printStackTrace();
		}
	}
}