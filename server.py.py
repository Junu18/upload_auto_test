from flask import Flask, render_template, request, redirect,make_response 
from aws import detect_labels_local_file as label
from werkzeug.utils import secure_filename
from aws import compare_faces 

# render_template > HTML 문서를 로드하는 역할
# 단 , templates 폴더에 있는 html만 바라볼 수 있다.

app = Flask(__name__)

# 서버 주소 / 
# "/"뒤에 무언가를 붙이면 맵핑되어서 실행
@app.route("/")
def index():
    return render_template("home.html")
    



@app.route("/mbti", methods = ["POST"])
def mbti():
    try:
        if request.method == "POST":
            mbti = request.form["mbti"]

            return f"당신의 MBTI는 {mbti}입니다"

    except:
        return "데이터 수신 실패"



@app.route("/login",methods=["GET"])
def login():
    try:
        if request.method == "GET":
            # login_id , login_pw 받아야함
            # get -> requst.args
        
            login_id = request.args["login_id"]
            login_pw = request.args["login_pw"]
            
            #redirect

            if (login_id == "jermain") and (login_pw=="1234"):
            
                response = make_response("로그인 성공")
                response.set_cookie("user",login_id)
            
                return response
            
            else:
                #로그인 -> 실패 경로로 다시 이동
                return redirect("/")


        # return f"{login_id}님 환영합니다."
    except:    
        return "로그인 실패"

# html 폴더 내 exam04.html을
# templates 폴더로 복사!!
@app.route("/exam04")
def exam04():
    return render_template("exam04.html")


@app.route("/login/success")
def login_success():
    
    login_id = request.cookies.get("user")
    return f"{login_id}님 환영합니다."



@app.route("/detect" , methods =["POST"])
def detect():
    try:
        if request.method == "POST":
            f= request.files["file"]
            filename = secure_filename(f.filename)
            # 외부에서 온 이미지 ,파일 등을
            # 마음대로 저장할 수 없음
            f.save("static/" + filename)
            r = label("static/" + filename)
            return r
            # 서버에 클라이언트가 보낸 이미지를 저장!

    except:
        return "객체 탐지 실패"


@app.route("/compare" , methods =["POST"])
def compare():
    try:
        if request.method == "POST":
            f1 = request.files["face_compare1"]
            f2 = request.files["face_compare2"]
            filename1 = secure_filename(f1.filename)
            filename2 = secure_filename(f2.filename)

            f1.save("static/" + filename1)
            f2.save("static/" + filename2)
            # r1 = compare_faces("static/" + filename1)
            # r2 = compare_faces("static/" + filename2)

            result = compare_faces("static/" + filename1, "static/" + filename2)
            return result
        # return r1,r2
        
    except:
            print("얼굴 비교 실패")
    




if __name__ == "__main__":

    # 1. host
    # 2. port

    app.run(host="0.0.0.0")




# 정답코드


# from flask import Flask, render_template
# from flask import request, redirect, make_response
# from aws import detect_labels_local_file as label
# from werkzeug.utils import secure_filename

# app = Flask(__name__)

# @app.route("/")
# def index():
#     return render_template("home.html")

# @app.route("/detect", methods=["POST"])
# def detect():
#     try:
#         if request.method == "POST":
#             f = request.files["file"]

#             filename = secure_filename(f.filename)
#             # 외부에서 온 이미지, 파일 등을
#             # 마음대로 저장할 수 없음
#             # 서버에 클라이언트가 보낸 이미지를 저장!!
#             f.save("static/" + filename)
#             r = label("static/" + filename)
#             return r
#     except:
#         return "감지 실패"

# @app.route("/mbti", methods=["POST"])
# def mbti():
#     try:
#         if request.method == "POST":
#             mbti = request.form["mbti"]

#             return f"당신의 MBTI는 {mbti}입니다"
#     except:
#         return "데이터 수신 실패"

# @app.route("/login", methods=["GET"])
# def login():
#     try:
#         if request.method == "GET":
#             # get -> request.args
#             login_id = request.args["login_id"]
#             login_pw = request.args["login_pw"]

#             if (login_id == "nayeho") and (login_pw == "1234"):
#                 # 로그인 성공 -> 로그인 성공 페이지로 이동
#                 # nayeho님 환영합니다
                
#                 response = make_response(redirect("/login/success"))
#                 response.set_cookie("user", login_id)

#                 return response
#             else:
#                 # 로그인 실패 -> / 경로로 다시 이동
#                 return redirect("/")
#     except:
#         return "로그인 실패"
    
# @app.route("/login/success", methods=["GET"])
# def login_success():

#     login_id = request.cookies.get("user")
#     return f"{login_id}님 환영합니다"

# if __name__ == "__main__":
#     app.run(host="0.0.0.0")
# # Ctrl + L하시면 터미널 클리어