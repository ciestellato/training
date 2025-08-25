package employeesDAO;

import java.io.Serializable;

//社員情報を入れるためのクラス（名前・IDなど）
public class Employee implements Serializable{

 // フィールド（社員のID・名前・年齢）
 private String id;
 private String name;
 private int age;

 // デフォルトコンストラクタ（空の社員オブジェクトを作るとき用）
 public Employee() {
 }

 // 引数付きコンストラクタ（ID・名前・年齢を指定して作る）
 public Employee(String id, String name, int age) {
     this.id = id;
     this.name = name;
     this.age = age;
 }

 // IDの取得メソッド
 public String getId() {
     return id;
 }

 // 名前の取得メソッド
 public String getName() {
     return name;
 }

 // 年齢の取得メソッド
 public int getAge() {
     return age;
 }

 // オブジェクトの中身を文字列で確認できるようにする（デバッグや表示用）
 @Override
 public String toString() {
     return "Employee{id='" + id + "', name='" + name + "', age=" + age + "}";
 }
}
