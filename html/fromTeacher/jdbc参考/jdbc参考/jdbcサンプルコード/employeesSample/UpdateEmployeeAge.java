package employeesSample;


import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class UpdateEmployeeAge {
	
    public static void main(String[] args) {
        // データベースと話すための準備
        try {
            Class.forName("org.h2.Driver");
        } catch (ClassNotFoundException e) {
            System.out.println("準備に失敗しました");
            return;
        }

        // データベースに接続して、情報を変更する
        try (Connection conn = DriverManager.getConnection(
                "jdbc:h2:tcp://localhost/~/example", // データベースの場所
                "sa",                                 // ユーザー名
                ""                                    // パスワード（空でOK）
        )) {
            // 「この人の年齢を変えてください」という文章を作る
            String sql = "UPDATE EMPLOYEES SET AGE = ? WHERE ID = ?";
            PreparedStatement pStmt = conn.prepareStatement(sql);

            // 新しい年齢と、誰の情報かをセットする
            pStmt.setInt(1, 30);           // 新しい年齢（例：30歳）
            pStmt.setString(2, "EMP001");  // 対象のID

            // 実行して変更する
            int rows = pStmt.executeUpdate();

            // 変更できたか確認
            if (rows > 0) {
                System.out.println("EMP001の年齢を変更しました");
            } else {
                System.out.println("EMP001が見つかりませんでした");
            }

        } catch (SQLException e) {
            System.out.println("変更中に問題が発生しました: " + e.getMessage());
        }
    }
}
