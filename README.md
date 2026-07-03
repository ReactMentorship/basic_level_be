# basic_level_be

A small **FastAPI** backend for the React mentorship app (`mfee-project-solution`).
It implements the exact REST contract the React frontend expects (Mongo-style
responses with `_id`, `__v` and ISO timestamps) using **in-memory storage** —
no database required. All data resets on restart.

## Requirements

- Python 3.10+ (tested on 3.14)

## Setup & run

From this folder (`basic_level_be`):

**1. Create the virtual environment** (only the first time):

```bash
python -m venv .venv
```

**2. Activate it** — use the line that matches your terminal:

```powershell
# Windows · PowerShell
.\.venv\Scripts\Activate.ps1
```

```bash
# Windows · Git Bash
source .venv/Scripts/activate

# macOS / Linux
source .venv/bin/activate
```

When it is active your prompt starts with `(.venv)`.

> **PowerShell only:** if you get an *"execution policy"* error, allow scripts for
> the current terminal session and activate again:
> ```powershell
> Set-ExecutionPolicy -Scope Process -ExecutionPolicy RemoteSigned
> ```

**3. Install the dependencies** (only the first time):

```bash
pip install -r requirements.txt
```

**4. Start the server:**

```bash
python run.py        # or: uvicorn app.main:app --reload --port 8000
```

The API runs at `http://localhost:8000` with routes under `/api`.
Interactive docs (Swagger UI): `http://localhost:8000/docs`.

> Tip: you can skip activation and run it with the venv's Python directly —
> PowerShell: `.\.venv\Scripts\python.exe run.py`

## Default credentials

A user is seeded on startup so you can log in immediately:

| username | password  |
| -------- | --------- |
| `admin`  | `admin123` |

Override via `SEED_USERNAME` / `SEED_PASSWORD` (see `.env.example`).

## Auth

All data routes require a Bearer token. Get one from `POST /api/auth/login`,
then send `Authorization: Bearer <accessToken>` on subsequent requests.

## Endpoints

Base URL: `http://localhost:8000/api`

### Auth
| Method | Path              | Body                                   | Returns            |
| ------ | ----------------- | -------------------------------------- | ------------------ |
| POST   | `/auth/register`  | `{username, password, firstname?, lastname?}` | `{message}` (201)  |
| POST   | `/auth/login`     | `{username, password}`                 | `{accessToken}`    |
| POST   | `/auth/logout`    | –                                      | `{message}`        |
| POST   | `/auth/refresh`   | –                                      | `{message, accessToken}` |

### Categories
| Method | Path                | Body       | Returns                 |
| ------ | ------------------- | ---------- | ----------------------- |
| GET    | `/categories`       | –          | `Category[]`            |
| POST   | `/categories`       | `{name}`   | `Category` (201)        |
| PATCH  | `/categories/{id}`  | `{name}`   | `Category`              |
| DELETE | `/categories/{id}`  | –          | `Category` (the deleted)|

### Posts
| Method | Path                          | Body                                      | Returns             |
| ------ | ----------------------------- | ----------------------------------------- | ------------------- |
| GET    | `/posts`                      | –                                         | `Post[]` (comments as ids) |
| GET    | `/posts/category/{catId}`     | –                                         | `Post[]`            |
| GET    | `/posts/{id}`                 | –                                         | `Post` (comments expanded) |
| POST   | `/posts`                      | `{title, image, description, category}`   | `Post` (201)        |
| PATCH  | `/posts/{id}`                 | `{title?, image?, description?, category?}`| `Post`              |
| DELETE | `/posts/{id}`                 | –                                         | `204 No Content`    |

> `category` in request bodies is a category **`_id`** (or empty for none).

### Comments
| Method | Path                        | Body                | Returns          |
| ------ | --------------------------- | ------------------- | ---------------- |
| POST   | `/posts/{id}/comments`      | `{author, content}` | `Comment` (201)  |

## Connecting the frontend

The React app (`mfee-project-solution/apps/react-app`) points at this backend via:

- `src/api/axios.ts` → `baseURL = http://localhost:8000/api`
- `src/context/AuthProvider.tsx` → token validation request

Start this backend first, then run `npm run start:react` in the frontend repo.
