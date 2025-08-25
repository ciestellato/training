package employeesSample;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class DeleteEmployee {
    public static void main(String[] args) {
        // データベースと話すための準備（通訳を呼ぶ）
        try {
            Class.forName("org.h2.Driver");
        } catch (ClassNotFoundException e) {
            System.out.println("準備に失敗しました");
            return;
        }

        // データベースに接続して、情報を削除する
        try (Connection conn = DriverManager.getConnection(
                "jdbc:h2:tcp://localhost/~/example", // データベースの場所
                "sa",                                 // ユーザー名（H2の初期設定）
                ""                                    // パスワード（空でOK）
        )) {
            // 「この人の情報を消してください」というお願い文を作る
            String sql = "DELETE FROM EMPLOYEES WHERE ID = ?";
            PreparedStatement pStmt = conn.prepareStatement(sql);

            // 誰の情報を消すかを指定する
            pStmt.setString(1, "EMP004");  // EMP004さんのIDをセット。 WHERE ID = "EMP004"

            // 実行して削除する
            int rows = pStmt.executeUpdate();

            // 削除できたか確認
            if (rows > 0) {
                System.out.println("EMP004の情報を削除しました");
            } else {
                System.out.println("EMP004が見つかりませんでした");
            }

        } catch (SQLException e) {
            System.out.println("削除中に問題が発生しました: " + e.getMessage());
        }
    }
}