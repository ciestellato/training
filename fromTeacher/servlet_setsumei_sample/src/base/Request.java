package base;

//顧客からのリクエスト情報を保持するクラス
public class Request {

	// 顧客の名前（例：山田太郎）
	String customerName;

	// リクエスト内容（例：商品の問い合わせ）
	String requestContents;

	// コンストラクタ：顧客名とリクエスト内容を受け取って初期化
	public Request(String customerName, String requestContents) {
		super(); // Objectクラスのコンストラクタ呼び出し（省略可能）
		this.customerName = customerName; // フィールドに顧客名をセット
		this.requestContents = requestContents; // フィールドにリクエスト内容をセット
	}

	// 顧客名を取得するゲッター
	public String getCustomerName() {
		return customerName;
	}

	// リクエスト内容を取得するゲッター
	public String getRequestContents() {
		return requestContents;
	}
}
