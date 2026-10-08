# API Contract — [TUFRater]

## Endpoint 1: Health Check

- **URL Path:** `/`
- **HTTP Method:** `GET`
- **What to send:** Nothing (no body, no headers needed).
- **Return (JSON):**

```json
{
  "message": "Server is running"
}
```

## Endpoint 2: Upload & Predict

- **URL Path:** `/files/upload`
- **HTTP Method:** `POST`
- **What to send:** A file payload. Because the backend code expects `file: UploadFile`, the frontend **must** send this using a `FormData` object (not raw JSON), with the key name set to `"file"`.
- **Return (JSON):**

```json
{
  "difficulty": "G10",
  "raw_score": 30.479356529529202,
  "features": {
    "tilecount": 3127,
    "bpm": 180,
    "twirl_count": 414,
    "speed_change_count": 112,
    "s_norm": 1072.1410297409657,
    "rt_score": 47643261.72964782,
    "p_var": 14.788941521738929
  }
}
```