from typing import Dict

import base64
import cv2
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pose_detector import PoseDetector
from angles import extract_angles

app = FastAPI()

# CORS 설정 (프론트엔드에서 접근 가능하도록)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 아주 간단한 인메모리 "DB" (서버 껐다 켜면 사라짐)
fake_users: Dict[str, str] = {}  # email -> password


# ==============================
# 요청/응답 모델 정의 (회원가입/로그인)
# ==============================
class SignupRequest(BaseModel):
    email: str
    password: str
    name: str  # 닉네임/이름


class SignupResponse(BaseModel):
    success: bool
    message: str


class LoginRequest(BaseModel):
    email: str
    password: str


class LoginResponse(BaseModel):
    success: bool
    message: str


# ==============================
# 포즈 분석용 요청/응답 모델
# ==============================
class PoseRequest(BaseModel):
    image_base64: str  # 클라이언트가 보내는 이미지(Base64)


class PoseResponse(BaseModel):
    knee_angle: float
    hip_angle: float
    torso_tilt: float
    feedback: str


# ==============================
# 기본 ping 엔드포인트
# ==============================
@app.get("/")
def read_root():
    return {"message": "hello from backend"}


# ==============================
# 회원가입 API
# ==============================
@app.post("/signup", response_model=SignupResponse)
def signup(req: SignupRequest):
    # 이미 존재하는 이메일이면 실패
    if req.email in fake_users:
        return SignupResponse(success=False, message="이미 가입된 이메일입니다.")

    # ⚠ 실제 서비스에서는 비밀번호를 반드시 해시해서 저장해야 하지만,
    # 지금은 데모라 그냥 평문으로 저장
    fake_users[req.email] = req.password
    print(f"[SIGNUP] {req.email} registered. total_users={len(fake_users)}")

    return SignupResponse(success=True, message="회원가입이 완료되었습니다.")


# ==============================
# 로그인 API
# ==============================
@app.post("/login", response_model=LoginResponse)
def login(req: LoginRequest):
    if req.email not in fake_users:
        return LoginResponse(success=False, message="가입되지 않은 이메일입니다.")

    if fake_users[req.email] != req.password:
        return LoginResponse(success=False, message="비밀번호가 올바르지 않습니다.")

    print(f"[LOGIN] {req.email} logged in.")
    return LoginResponse(success=True, message="로그인 성공")


# ==============================
# 포즈 분석 API
# ==============================
@app.post("/pose/analyze", response_model=PoseResponse)
def analyze_pose(req: PoseRequest):

    # 1. Base64 → OpenCV 이미지
    img_bytes = base64.b64decode(req.image_base64)
    # Base64 디코딩된 바이트를 numpy 배열로 변환
    # NumPy의 frombuffer 함수 사용 (일부 버전에서는 없을 수 있음)
    try:
        np_arr = np.frombuffer(img_bytes, dtype=np.uint8)
    except (AttributeError, TypeError):
        # 대안: bytearray를 numpy 배열로 변환
        np_arr = np.array(bytearray(img_bytes), dtype=np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return PoseResponse(
            knee_angle=-1, hip_angle=-1, torso_tilt=-1,
            feedback="이미지를 처리할 수 없습니다."
        )

    # 2. Pose detection
    pose = PoseDetector(model_complexity=1)
    lms = pose.process(frame)

    if lms is None:
        return PoseResponse(
            knee_angle=-1, hip_angle=-1, torso_tilt=-1,
            feedback="사람이 화면에 정확히 나타나지 않습니다."
        )

    kpts = pose.to_numpy()

    # 3. 각도 계산
    h, w = frame.shape[:2]
    ang = extract_angles(kpts, side='right', w=w, h=h)

    knee = float(ang.get("knee", -1))
    hip = float(ang.get("hip", -1))
    tilt = float(ang.get("torso_tilt", -1))

    # 4. 피드백 생성 로직 (예시)
    if knee < 40:
        fb = "너무 깊어요! 무릎을 조금 펴주세요."
    elif knee < 70:
        fb = "좋아요! 안정적인 자세입니다."
    elif knee < 110:
        fb = "조금 더 내려가보세요!"
    else:
        fb = "무릎을 더 굽혀야 해요!"

    # 5. 최종 응답
    return PoseResponse(
        knee_angle=knee,
        hip_angle=hip,
        torso_tilt=tilt,
        feedback=fb
    )
