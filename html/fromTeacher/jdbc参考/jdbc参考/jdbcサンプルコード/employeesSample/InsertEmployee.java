package employeesSample;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class InsertEmployee {
    public static void main(String[] args) {
    	
        // データベースと話すための準備（ドライバーを読み込む）
        try {
            Class.forName("org.h2.Driver");
        } catch (ClassNotFoundException e) {
            System.out.println("データベースの準備に失敗しました");
            return;
        }

        // データベースに接続して、情報を登録する
        try (Connection conn = DriverManager.getConnection(
                "jdbc:h2:tcp://localhost/~/example", // データベースの場所
                "sa",                                 // ユーザー名（H2の初期設定）
                ""                                    // パスワード（空でOK）
        )) {
        	
            // 登録する文章（SQL）を作る。？はあとで値を埋める場所
            String sql = "INSERT INTO EMPLOYEES (ID, NAME, AGE) VALUES (?, ?, ?)";
            PreparedStatement pStmt = conn.prepareStatement(sql);

            // 1人目の情報を VALUES (?, ?, ?）にセットして登録=> VALUES（"EMP003", "鈴木 太郎", 23）
            pStmt.setString(1, "EMP003");         // ID
            pStmt.setString(2, "鈴木 太郎");         // 名前
            pStmt.setInt(3, 23);                  // 年齢
            pStmt.executeUpdate();                // 実行して登録

            // 2人目の情報をセットして登録
            pStmt.setString(1, "EMP004");
            pStmt.setString(2, "田中 洋子");
            pStmt.setInt(3, 22);
            pStmt.executeUpdate();

            System.out.println("2人の情報を登録しました");

        } catch (SQLException e) {
            System.out.println("登録中に問題が発生しました: " + e.getMessage());
        }
    }
}
