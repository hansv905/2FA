from flask import Flask, request, session, render_template, redirect, url_for
import pyotp
import qrcode
import base64
from io import BytesIO
import logging
import colorlog

# 컬러 로깅 설정
handler = colorlog.StreamHandler()
handler.setFormatter(colorlog.ColoredFormatter(
    '%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    log_colors={
        'DEBUG': 'cyan',
        'INFO': 'red',  # INFO 레벨을 빨간색으로 설정
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
))

logger = colorlog.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

app = Flask(__name__)
app.secret_key = 'your-secret-key'

user_secrets = {}

@app.route('/setup_2fa', methods=['GET'])
def setup_2fa():
    # secret = pyotp.random_base32()
    secret = "7FTW7AJPDK7BM4YB46OIY7B4TYM3YYKL"
    secret = "ABCDEFGH22345678ABCDEFGH22345678" #Base32 인코딩 규칙 준수 필요 A-Z, 2-7
    user_secrets['user_id'] = secret

    
    totp = pyotp.TOTP(secret)
    provisioning_uri = totp.provisioning_uri(
        "user@example.com",
        issuer_name="YourApp"
    )
    
    # QR 코드 생성 및 이미지 변환
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # 이미지를 바이트로 변환
    buffered = BytesIO()
    img.save(buffered)  # format 인자 제거
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return render_template('index.html', 
                         secret=secret,
                         qr_code=img_str)

@app.route('/verify_2fa', methods=['POST'])
def verify_2fa():
    code = request.form.get('code')
    secret = user_secrets.get('user_id')
    
    totp = pyotp.TOTP(secret)
    
    if totp.verify(code):
        session['2fa_verified'] = True
        return "2FA 인증 성공!"
    else:
        return "잘못된 코드입니다."

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3002, debug=True)