# RAG Learning Project

## 프로젝트 개요

사용자가 PDF, DOCX, PPTX 등의 학습 문서를 업로드하면
RAG 기반 AI가 해당 문서를 기반으로 질문에 답하고,
요약과 퀴즈를 생성해 학습을 지원하는 서비스.

개발자 전용 서비스가 아니라
모든 분야의 사용자가 자신의 문서를 활용하여 학습할 수 있도록 한다.

---

## 기술 스택

Frontend
- Flutter

Backend
- Python
- FastAPI

Database
- MySQL

ORM
- SQLAlchemy

AI
- OpenAI API

RAG
- 문서 파싱
- Chunking
- Embedding
- Vector Search
- LLM Answer Generation

---

## Backend Structure

app/
├── models/
├── schemas/
├── routers/
├── services/
│   ├── user_service.py
│   ├── document_service.py
│   ├── chat_service.py
│   ├── summary_service.py
│   ├── quiz_service.py
│   └── rag_service.py
├── auth.py
├── config.py
└── database.py

main.py

---

## Architecture Rules

routers
- HTTP 요청 및 응답 처리
- 비즈니스 로직을 직접 작성하지 않는다.

services
- 비즈니스 로직 담당
- DB 처리 및 RAG 로직 호출

models
- SQLAlchemy ORM 모델

schemas
- Pydantic request / response schema

database.py
- SQLAlchemy engine
- SessionLocal
- Base
- get_db()

config.py
- .env 환경변수 관리

auth.py
- 비밀번호 해싱
- JWT 인증

---

## 주요 기능

### 사용자
- 회원가입
- 로그인
- 로그아웃
- 소셜 로그인

### 문서
- 문서 업로드
- 문서 목록
- 문서 삭제
- 문서 그룹 관리

### RAG
- 문서 텍스트 추출
- Chunk 생성
- Embedding 생성
- 유사 Chunk 검색
- 문서 기반 AI 답변
- 답변 출처 제공

### 채팅
- 채팅 세션
- 메시지 저장
- 여러 문서 기반 질문

### 요약
- 문서 요약 생성
- 요약 근거 저장

### 퀴즈
- 퀴즈 생성
- 문제 생성
- 선택지 저장
- 문제 출처 저장
- 사용자 답변
- 퀴즈 시도 기록

### 학습
- 학습 기록 저장

---

## Database Tables

현재 설계된 주요 테이블:

- users
- social_accounts
- social_providers

- documents
- document_groups
- document_group_items
- document_chunks
- embeddings

- chat_sessions
- chat_session_documents
- chat_messages
- message_sources

- summaries
- summary_sources

- quizzes
- quiz_questions
- question_options
- question_sources
- quiz_attempts
- quiz_answers

- learning_history

---

## 개발 진행 상황

완료:
- 프로젝트 기획
- 주요 기능 정의
- DB 설계
- MySQL 데이터베이스 생성
- FastAPI 가상환경 구성
- FastAPI 서버 실행
- 프로젝트 기본 폴더 구조 구성
- SQLAlchemy DB 연결 코드 작성

현재 작업:
- Backend 구현 시작

다음 작업:
1. User ORM Model 작성
2. User Pydantic Schema 작성
3. User Service 작성
4. 회원가입 Router 작성
5. Swagger 회원가입 테스트
6. 로그인 / JWT 인증 구현

---

## 개발 우선순위

1. 회원가입 / 로그인
2. 문서 업로드
3. 문서 파싱
4. Chunking
5. Embedding
6. Vector Search
7. RAG 질문/답변
8. 출처 표시
9. 요약
10. 퀴즈
11. Flutter 연동

---

## 코딩 규칙

- Router에 복잡한 비즈니스 로직을 작성하지 않는다.
- DB 관련 작업은 Service 계층에서 처리한다.
- Pydantic Schema와 SQLAlchemy Model을 분리한다.
- 비밀번호 평문을 DB에 저장하지 않는다.
- API Key와 DB 비밀번호는 .env로 관리한다.
- .env는 Git에 커밋하지 않는다.
- 기능별로 파일을 분리한다.