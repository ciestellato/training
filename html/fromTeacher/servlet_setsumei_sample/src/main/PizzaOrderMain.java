package main;

//必要なクラスをインポート（リクエスト・レスポンス・注文処理）
import base.Request;
import base.Response;
import pizzaShop.PizzaOrderServlet;

//ピザ注文処理のメインクラス（アプリケーションの起点）
public class PizzaOrderMain {

 // Tomcatアプリケーションがクライアントブラウザからリクエストを受け取った際の動作をシミュレーション
 public static void main(String[] args) {

     // 顧客からの注文情報を作成（住所＋氏名、注文内容）
     Request request = new Request("新宿区西新宿1-2-3：山田太郎", "マルゲリータピザ・2枚");

     // 応答メッセージを格納するレスポンスオブジェクトを生成
     Response response = new Response();

     // ピザ注文処理を担当するサーブレットを生成
     PizzaOrderServlet pizzaServlet = new PizzaOrderServlet();

     // サーブレットに注文処理を依頼（リクエストとレスポンスを渡す）
     pizzaServlet.order(request, response);

     // 顧客向けの応答メッセージを文字列として取得
     String messageToCustomer = response.toString();

     // 応答メッセージをコンソールに出力
     System.out.println(messageToCustomer);
 }
}
