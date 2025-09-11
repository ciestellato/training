import pytest # Fixtureのために必要なインポート
from ex11_3 import Employee

# インスタンスを生成してテスト ---------------------------------------
def test_give_default_raise():
    """デフォルト昇給のテスト"""
    employee = Employee("hoge", "foo", 6000000)
    employee.give_raise()
    assert employee.salary == 6500000

def test_give_custom_raise():
    """カスタム昇給のテスト"""
    employee = Employee("hoge", "foo", 6000000)
    employee.give_raise(1000000)
    assert employee.salary == 7000000

# Fixtureを使用してテスト --------------------
@pytest.fixture # fixtureデコレーターを新しい関数に適用
def employee():
    """Employeeオブジェクトを作成して返す"""
    employee = Employee("hoge", "foo", 6000000)
    return employee

# テスト関数の引数がfixtureデコレーターがついた関数の名前と一致すると
# fixtureが自動的に実行され、その戻り値がテスト関数に渡される
def test_give_default_raise_fixture(employee):
    """デフォルト昇給のテスト"""
    employee.give_raise()
    assert employee.salary == 6500000

def test_give_custom_raise_fixture(employee):
    """カスタム昇給のテスト"""
    employee.give_raise(1000000)
    assert employee.salary == 7000000