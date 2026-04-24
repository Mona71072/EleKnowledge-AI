---
status: production
phase: 1
last-verified: 2026-04-24
related-code: lambda/auth/
---

# 認証API

> spec.md §7.1 から切り出し。Phase 1 で実装済みの認証系エンドポイントを記載する。

**Base URL:** `https://xxxxx.execute-api.us-east-1.amazonaws.com/prod`

## POST /auth/signup
ユーザー登録

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "message": "確認コードをメールに送信しました",
  "userId": "xxxxx"
}
```

## POST /auth/login
ログイン

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response:**
```json
{
  "accessToken": "eyJxx...",
  "refreshToken": "eyJxx...",
  "idToken": "eyJxx...",
  "expiresIn": 3600
}
```
