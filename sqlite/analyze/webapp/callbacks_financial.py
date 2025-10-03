from dash import Output, Input, State, callback
import dash
import sqlite3
import pandas as pd
import plotly.express as px
from dash import html, dcc
from edinet_config import Config

def register_financial_callbacks(app):
    """財務関係のコールバック"""
        # 会社名のあいまい検索と候補表示
    @callback(
        Output('company-dropdown', 'options'),
        Input('company-search-input', 'value'),
        prevent_initial_call=True
    )
    def search_company_candidates(search_text):
        if not search_text:
            raise dash.exceptions.PreventUpdate

        conn = sqlite3.connect(Config.DB_PATH)

        if search_text.isdigit() and len(search_text) == 4:
            # 証券コードによる検索
            query = """
                SELECT DISTINCT filerName, secCode
                FROM edinet_document_summaries
                WHERE secCode = ?
            """
            df = pd.read_sql_query(query, conn, params=[search_text])
        else:
            # 会社名によるあいまい検索
            query = """
                SELECT DISTINCT filerName, secCode
                FROM edinet_document_summaries
                WHERE filerName LIKE ?
                ORDER BY filerName
            """
            df = pd.read_sql_query(query, conn, params=[f"%{search_text}%"])

        conn.close()

        return [
        {'label': f"{row['filerName']} ({row['secCode']})", 'value': row['secCode']}
        for _, row in df.iterrows()
        if pd.notnull(row['secCode'])
        ]

    # 選択された会社の財務データ取得
    @callback(
        Output('financial-tabs-container', 'children'),
        Input('company-dropdown', 'value'),
        prevent_initial_call=True
    )
    def display_financial_tabs(sec_code):
        if not sec_code:
            raise dash.exceptions.PreventUpdate

        conn = sqlite3.connect(Config.DB_PATH)
        query = """
            SELECT fd.*, s.periodEnd
            FROM edinet_financial_data fd
            JOIN edinet_document_summaries s ON fd.docID = s.docID
            WHERE s.secCode = ?
            ORDER BY s.periodEnd DESC
        """
        df = pd.read_sql_query(query, conn, params=[sec_code])
        conn.close()

        if df.empty:
            return html.Div("財務データが見つかりませんでした。")

        tabs = []
        for period_end, group in df.groupby('periodEnd'):
            tab_label = f"{pd.to_datetime(period_end).year}年{pd.to_datetime(period_end).month}月期"
            table = dash.dash_table.DataTable(
                columns=[{"name": i, "id": i} for i in group.columns],
                data=group.to_dict('records'),
                page_size=15
            )
            tabs.append(dcc.Tab(label=tab_label, children=[table]))

        return dcc.Tabs(children=tabs)

    # 財務データ表示コールバック
    @callback(
        Output('financial-data-output', 'children'),
        Output('financial-data-graph', 'figure'),
        Input('fetch-financial-data-button', 'n_clicks'),
        State('company-search-input', 'value'),
        State('period-end-input', 'value'),
        prevent_initial_call=True
    )
    def fetch_and_display_financial_data(n_clicks, company_search, period_end):
        if n_clicks > 0:
            if not company_search and not period_end:
                return html.Div("会社名または証券コード、会計期間終了日のいずれかを入力してください。", style={'color': 'red'}), {}

            conn = None
            try:
                conn = sqlite3.connect(Config.DB_PATH)
                # 検索条件に基づいてSQLクエリを構築
                sql_query = """
                    SELECT
                        s.filerName AS 会社名,
                        s.secCode AS 証券コード,
                        s.docDescription AS 書類概要,
                        s.periodStart AS 会計期間_開始日,
                        s.periodEnd AS 会計期間_終了日,
                        fd.accountName AS 勘定科目名,
                        fd.amount AS 金額,
                        fd.unit AS 単位,
                        fd.currency AS 通貨
                    FROM
                        edinet_financial_data AS fd
                    JOIN
                        edinet_document_summaries AS s
                    ON
                        fd.docID = s.docID
                    WHERE 1=1
                """
                params = []

                if company_search:
                    if company_search.isdigit() and len(company_search) == 4: # 証券コードを想定
                        sql_query += " AND s.secCode = ?"
                        params.append(company_search)
                    else: # 会社名を想定
                        sql_query += " AND s.filerName LIKE ?"
                        params.append(f"%{company_search}%")
                
                if period_end:
                    sql_query += " AND s.periodEnd = ?"
                    params.append(period_end)
                
                sql_query += """
                    AND fd.accountName IN (
                        '売上高', '営業利益', '経常利益', '当期純利益',
                        '流動資産合計', '固定資産合計', '資産合計',
                        '流動負債合計', '固定負債合計', '負債合計',
                        '純資産合計', '負債純資産合計'
                    )
                    ORDER BY s.periodEnd DESC, fd.accountName
                """
                
                df = pd.read_sql_query(sql_query, conn, params=params)

                if df.empty:
                    return html.Div("指定された条件の財務データは見つかりませんでした。", style={'color': 'orange'}), {}

                # データフレーム表示
                table = dash.dash_table.DataTable(
                    id='table',
                    columns=[{"name": i, "id": i} for i in df.columns],
                    data=df.to_dict('records'),
                    page_size=15,
                    style_table={'overflowX': 'auto'}
                )

                # グラフ表示（例: 棒グラフ）
                # 複数行のデータがある場合を考慮
                fig = px.bar(
                    df,
                    x="勘定科目名",
                    y="金額",
                    color="会社名",
                    barmode="group",
                    title=f"{df['会社名'].iloc[0]} のBS/PL概要 ({df['会計期間_終了日'].iloc[0]})",
                    text="金額" # 金額を棒グラフの上に表示
                )
                # 金額が大きい場合に単位を調整するなどの整形は別途必要
                fig.update_traces(texttemplate='%{text:,.0f}', textposition='outside')
                fig.update_layout(uniformtext_minsize=8, uniformtext_mode='hide')

                return html.Div([
                    html.H3("取得結果"),
                    table
                ]), fig

            except sqlite3.Error as e:
                return html.Div(f"データベースエラー: {e}", style={'color': 'red'}), {}
            except Exception as e:
                return html.Div(f"データの取得・表示中にエラーが発生しました: {e}", style={'color': 'red'}), {}
            finally:
                if conn:
                    conn.close()
        return "", {}
