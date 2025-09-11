from survey import AnonymousSurvey

def test_AS():
    question = "最初に勉強した言語は何ですか？"
    language_survey = AnonymousSurvey(question)
    # 英語 という回答を追加
    language_survey.store_response("英語")
    # 回答リストの中に"英語"がある
    assert "英語" in language_survey.responses