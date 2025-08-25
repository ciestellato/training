package muttersSample;

import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.SQLException;

public class InsertMutter {
    public static void main(String[] args) {
    	
        // データベースと話すための準備（ドライバーを読み込む）
        try {
            Class.forName("org.h2.Driver");
        } catch (ClassNotFoundException e) {
            System.out.println("データベースの準備に失敗しました");
            return;
        }

        // dokoTsubuデータベースに接続して、情報を登録する
        try (Connection conn = DriverManager.getConnection(
                "jdbc:h2:tcp://localhost/~/dokoTsubu", // データベースの場所
                "sa",                                 // ユーザー名（H2の初期設定）
                ""                                    // パスワード（空でOK）
        )) {
        	
            // ●ここを修正：登録する文章（SQL）を作る。？はあとで値を埋める場所
            String sql = "INSERT INTO テーブル名 (列名...) VALUES (?, ?, ?)";
            PreparedStatement pStmt = conn.prepareStatement(sql);

            //  ●ここを修正：1つのつぶやき情報を VALUES (?, ?, ?）にセットして登録
            pStmt.setString(1, "EMP003");         // ID
            pStmt.setString(2, "鈴木 太郎");         // 名前
            pStmt.setInt(3, 23);                  // 年齢
            pStmt.executeUpdate();                // 実行して登録


            System.out.println("1つのつぶやき情報を登録しました");

        } catch (SQLException e) {
            System.out.println("登録中に問題が発生しました: " + e.getMessage());
        }
    }
}
