# Metaculus API Reference

## Authentication

```bash
# Token-based auth
Authorization: Token YOUR_API_KEY

# Or via header
-H "Authorization: Token 04a3c97a97707c9edcbc9eb5a67c3a1d7212ac7f"
```

## Base URLs

```
Production: https://www.metaculus.com/api2/
Legacy:     https://www.metaculus.com/api/
```

## Endpoints

### Questions

#### List Questions
```bash
GET /api2/questions/
```

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `limit` | int | Results per page (default 10) |
| `offset` | int | Pagination offset |
| `status` | string | `open`, `closed`, `resolved` |
| `project` | int | Tournament/project ID |
| `type` | string | `binary`, `numeric`, `multiple_choice`, `date` |
| `search` | string | Search query |

**Response:**
```json
{
  "count": 1234,
  "next": "https://...",
  "results": [
    {
      "id": 12345,
      "title": "Will X happen by 2026?",
      "type": "binary",
      "status": "open",
      "close_time": "2026-09-06T00:00:00Z",
      "resolve_time": "2026-12-31T00:00:00Z",
      "project_ids": [3876],
      "community_prediction": 0.65,
      "num_forecasts": 42
    }
  ]
}
```

#### Get Question
```bash
GET /api2/questions/{id}/
```

#### Submit Forecast (Binary)
```bash
POST /api2/questions/{id}/forecast/
Content-Type: application/json

{"probability": 0.65}
```

#### Submit Forecast (Numeric/CDF)
```bash
POST /api2/questions/{id}/forecast/
Content-Type: application/json

{"continuous_cdf": [0.0, 0.01, 0.02, ..., 1.0]}  // 201 points
```

#### Submit Forecast (Multiple Choice)
```bash
POST /api2/questions/{id}/forecast/
Content-Type: application/json

{"probabilities": {"option1": 0.3, "option2": 0.5, "option3": 0.2}}
```

#### Get Forecasts
```bash
GET /api2/questions/{id}/forecasts/
```

### Tournaments

#### Get Tournament
```bash
GET /api/projects/{id}/
```

#### Get Tournament Leaderboard
```bash
GET /api/leaderboards/project/{id}/
```

**Parameters:**
| Param | Type | Description |
|-------|------|-------------|
| `limit` | int | Entries per page |
| `offset` | int | Pagination offset |
| `score_type` | string | `peer`, `baseline`, `spot_peer`, `spot_baseline` |

**Response:**
```json
{
  "leaderboard": {
    "id": 123,
    "name": "FutureEval Tournament",
    "score_type": "peer_tournament",
    "project": {
      "id": 3876,
      "name": "FutureEval",
      "slug": "futureeval",
      "prize_pool": "50000.00",
      "finalized": false
    }
  },
  "entries": [
    {
      "user": {
        "id": 12345,
        "username": "xev0",
        "is_bot": true
      },
      "rank": 1,
      "score": 123.45,
      "score_ci_lower": 120.0,
      "score_ci_upper": 126.9,
      "coverage": 0.95,
      "n_questions": 312,
      "medal": "gold",
      "prize": 5000.00
    }
  ]
}
```

#### Get Global Leaderboard
```bash
GET /api/leaderboards/global/?limit=100
```

### User

#### Current User
```bash
GET /api/user/
```

#### User Profile
```bash
GET /api2/users/{id}/
GET /api2/users/{username}/
```

### Data Downloads

#### Available Datasets
```bash
GET /api/data/
```

#### Score Data
```bash
GET /api/scores/
```

## Rate Limits

- Anonymous: 30 requests/minute
- Authenticated: 300 requests/minute
- Bot accounts: 600 requests/minute (if allowed)

## Error Codes

| Code | Meaning |
|------|---------|
| 400 | Bad request (invalid forecast format) |
| 401 | Unauthorized (bad token) |
| 403 | Forbidden (question closed, bot not allowed) |
| 404 | Not found |
| 429 | Rate limited |

## Python SDK Example

```python
import requests

class MetaculusClient:
    def __init__(self, token):
        self.base = "https://www.metaculus.com/api2"
        self.headers = {"Authorization": f"Token {token}"}
    
    def list_questions(self, status="open", limit=10):
        r = requests.get(f"{self.base}/questions/", 
                        headers=self.headers,
                        params={"status": status, "limit": limit})
        return r.json()
    
    def forecast_binary(self, question_id, probability):
        r = requests.post(f"{self.base}/questions/{question_id}/forecast/",
                         headers=self.headers,
                         json={"probability": probability})
        return r.json()
    
    def forecast_numeric(self, question_id, cdf_201_points):
        r = requests.post(f"{self.base}/questions/{question_id}/forecast/",
                         headers=self.headers,
                         json={"continuous_cdf": cdf_201_points})
        return r.json()
    
    def get_leaderboard(self, project_id, limit=100):
        r = requests.get(f"https://www.metaculus.com/api/leaderboards/project/{project_id}/",
                        headers=self.headers,
                        params={"limit": limit})
        return r.json()

# Usage
client = MetaculusClient("04a3c97a97707c9edcbc9eb5a67c3a1d7212ac7f")
questions = client.list_questions(status="open", limit=50)
leaderboard = client.get_leaderboard(project_id=3876)
```
