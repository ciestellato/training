package base;

//店舗からの応答メッセージを管理するクラス
public class Response {

	// 店舗名（例：ABCショップ）
	String shopName;

	// 応答メッセージを蓄積するための可変文字列（appendで追記可能）
	StringBuilder responseMessage = new StringBuilder();

	// 店舗名を設定するセッター
	public void setShopName(String shopName) {
		this.shopName = shopName;
	}

	// 応答メッセージにテキストを追加するメソッド
	public void print(String text) {
		this.responseMessage.append(text);
	}

	// 応答メッセージの内容を文字列として返す（デバッグやログ出力に便利）
	@Override
	public String toString() {
		return "Response [shopName=" + shopName + ", responseMessage=" + responseMessage + "]";
	}
}
