package base;

//注文処理の基本的な処理を定義する抽象クラス
public abstract class OrderServlet {

	// 注文処理を行うメソッド（具象クラスで具体的な処理を実装）
	public void order(Request req, Response res) {
		// 実装はサブクラスに委ねる
	}

	// 注文キャンセル処理を行うメソッド（具象クラスで具体的な処理を実装）
	public void cancel(Request req, Response res) {
		// 実装はサブクラスに委ねる
	}
}
