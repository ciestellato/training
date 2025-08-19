package pizzaShop;

//必要なクラスをインポート（注文処理の基底クラスとリクエスト・レスポンスモデル）
import base.OrderServlet;
import base.Request;
import base.Response;

//ピザ注文専用のサーブレットクラス（OrderServletを継承）
public class PizzaOrderServlet extends OrderServlet {

	// 注文処理をオーバーライド（記述）して、ピザ注文に対応
	@Override
	public void order(Request req, Response res) {
		
		// 顧客名と注文内容を取得
		String name = req.getCustomerName();
		String order = req.getRequestContents();

		// ※ここにピザスタッフへのオーダー伝達処理を実装する想定（未実装）

		// レスポンスに店舗名を設定
		res.setShopName("ドミノピザ新宿店\n");

		// 顧客向けの応答メッセージを構築（改行コードはエスケープされている）
		res.print(name + "様。\n");
		res.print(order + "を承りました。\n");
		res.print("19;00の配達予定です。\n");
		res.print("ご注文ありがとうございました。");
		
	}
}
