package employeesDAO;

//社員情報をデータベースから取り出すためのクラス
import java.sql.Connection;
import java.sql.DriverManager;
import java.sql.PreparedStatement;
import java.sql.ResultSet;
import java.sql.SQLException;
import java.util.ArrayList;
import java.util.List;

public class EmployeesDAO {

	/**
	 * 社員一覧を取得する
	 * @return Employeeデータのリスト
	 */
	public List<Employee> findAll() { // 社員一覧を取得するメソッド

		List<Employee> list = new ArrayList<>(); // ●結果を格納するリストを用意

		try {
			// JDBCドライバを読み込む（H2データベース用）
			Class.forName("org.h2.Driver");
		} catch (ClassNotFoundException e) {
			// ドライバが見つからなかった場合の処理
			System.out.println("JDBCドライバが見つかりません");
			return list; // 空のリストを返して終了
		}

		// データベースに接続して社員情報を取得
		try (Connection conn = DriverManager.getConnection(
				"jdbc:h2:tcp://localhost/~/example", // データベースの場所
				"sa", // ユーザー名（初期設定）
				"" // パスワード（空）
		)) {

			// 社員情報（ID・名前・年齢）を取得するSQL文
			String sql = "SELECT ID, NAME, AGE FROM EMPLOYEES";

			// SQL文を実行するための準備
			PreparedStatement pStmt = conn.prepareStatement(sql);

			// SQL文を実行し、結果表（ResultSet）を取得
			ResultSet rs = pStmt.executeQuery();

			// 結果表に格納されたレコードを1行ずつ処理
			while (rs.next()) {
				String id = rs.getString("ID"); // IDを取得
				String name = rs.getString("NAME"); // 名前を取得
				int age = rs.getInt("AGE"); // 年齢を取得

				// ●取得した情報をもとにEmployeeオブジェクトを作成
				Employee emp = new Employee(id, name, age);
				System.out.println(emp);

				// ●作成したオブジェクトをリストに追加
				list.add(emp);
				System.out.println(list);
			}

		} catch (SQLException e) {
			// データベース操作で問題が起きた場合の処理
			System.out.println("データ取得に失敗しました: " + e.getMessage());
			return null;// ●検索失敗時は、nullを返す
		}

		return list; // ●社員情報が入ったリストを返す
	}

	
	/**
	 * 社員情報を追加（INSERT）する
	 * @param employee
	 * @return 追加成功時true、失敗時false
	 */
	public boolean create(Employee employee) {
		try {
			// JDBCドライバの読み込み（H2データベース用）
			Class.forName("org.h2.Driver");
		} catch (ClassNotFoundException e) {
			// ドライバが見つからない場合
			System.out.println("JDBCドライバが見つかりません");
			return false;
		}

		// データベースに接続してINSERT文を実行
		try (Connection conn = DriverManager.getConnection(
				"jdbc:h2:tcp://localhost/~/example", // データベースの場所
				"sa", // ユーザー名
				"" // パスワード（空）
		)) {
			// 社員情報を追加するSQL文（?は後で値を入れる場所）
			String sql = "INSERT INTO EMPLOYEES (ID, NAME, AGE) VALUES (?, ?, ?)";

			// SQL文を準備
			PreparedStatement pStmt = conn.prepareStatement(sql);

			// ? に値をセット（Employeeオブジェクトから取得）
			pStmt.setString(1, employee.getId());
			pStmt.setString(2, employee.getName());
			pStmt.setInt(3, employee.getAge());

			// SQL文を実行（戻り値は追加された行数）
			int result = pStmt.executeUpdate();

			// 1件以上追加されたら成功とみなす
			return result > 0;

		} catch (SQLException e) {
			// データベース操作で問題が起きた場合
			System.out.println("データ追加に失敗しました: " + e.getMessage());
			return false;
		}
	}
}