@echo off
echo �z�z���ꂽDjango�̉��z���̃Z�b�g�A�b�v���J�n���܂��B
REM ���z�����쐬
python -m venv venv

REM ���z����L����
call venv\Scripts\activate

REM �ˑ��p�b�P�[�W���C���X�g�[��
pip install -r requirements.txt

REM �I�����b�Z�[�W
echo ���z���̃Z�b�g�A�b�v���������܂����B
pause