# REST API

The Studentenportal provides a REST API under `/api/v1/`. `GET` on the root
lists all endpoints:

```
http://localhost:8000/api/v1/
```

All responses are JSON. List endpoints are paginated
(`LimitOffsetPagination`, page size 20) and return

```json
{"count": 42, "next": "...", "previous": null, "results": [...]}
```

## Authentication

Two authentication methods are supported:

### Basic Authentication

Use your website credentials (username = your `@ost.ch` e-mail prefix,
e.g. `vorname.nachname`; the full e-mail also works) with any HTTP client:

```bash
curl -u vorname.nachname:passwort http://localhost:8000/api/v1/users
```

For development, the test users from [CONTRIBUTING.md](CONTRIBUTING.md) can be
used, e.g. `user1` / `user1`.

### Session Authentication

If you are logged in on the website, your browser session is also accepted by
the API. This is how the Browsable API at `http://localhost:8000/api/v1/`
works. Write requests (POST/PATCH/PUT/DELETE) require a valid CSRF token,
exactly like the website forms.

## Access rules

- **Anonymous** users can read what the website shows without login:
  documents (public only), document categories, events and tipps
  (including their comments).
- **Authenticated** users can additionally read users, lecturers and quotes,
  and all (non-public) documents.
- **Creating, editing and deleting** always requires authentication.
  You can only modify objects that were created through your account
  (403 otherwise). Author/uploader fields are read-only and set
  automatically.
- The e-mail address of a user is only included in their own profile.

## Endpoints

| Endpoint | Methods | Access |
| --- | --- | --- |
| `/` | GET | public |
| `users` | GET | authenticated |
| `users/{pk}` | GET, PUT, PATCH | authenticated; write: own profile only |
| `lecturers` | GET | authenticated |
| `lecturers/{pk}` | GET | authenticated |
| `lecturers/{pk}/rate` | POST | authenticated |
| `quotes` | GET, POST | authenticated |
| `quotes/{pk}` | GET, PUT, PATCH, DELETE | authenticated; write: author only |
| `quotes/{pk}/vote` | POST | authenticated |
| `documents` | GET, POST | GET: public (public documents only); POST: authenticated |
| `documents/{pk}` | GET, PUT, PATCH, DELETE | GET: public (public documents only); write: uploader only |
| `documents/{pk}/rate` | POST | authenticated |
| `documentcategories` | GET, POST | GET: public; POST: authenticated |
| `documentcategories/{pk}` | GET | public |
| `events` | GET, POST | GET: public; POST: authenticated |
| `events/{pk}` | GET, PUT, PATCH, DELETE | GET: public; write: author only |
| `tipps` | GET, POST | GET: public; POST: authenticated |
| `tipps/{pk}` | GET, PUT, PATCH, DELETE | GET: public; write: author only |
| `tipps/{pk}/vote` | POST | authenticated |
| `tipps/{pk}/comments` | GET, POST | GET: public; POST: authenticated |
| `tipps/{pk}/comments/{pk}` | GET, PUT, PATCH, DELETE | GET: public; write: author only |

All paths are relative to `/api/v1/`.

## Query parameters

All list endpoints support:

- `?q=term` — search (fields depend on the endpoint, e.g. name and
  description for documents)
- `?ordering=field` — sort by a model field, prefix `-` for descending
  (e.g. `?ordering=-upload_date` for documents, `?ordering=-date` for tipps)
- `?limit=N&offset=M` — pagination

## Examples

### Read a public list

```bash
curl "http://localhost:8000/api/v1/documents?ordering=-upload_date"
```

### Update your own event (JSON)

```bash
curl -u user1:user1 -X PATCH \
     -H "Content-Type: application/json" \
     -d '{"summary": "Neuer Titel"}' \
     http://localhost:8000/api/v1/events/12
```

### Upload a document (multipart form data)

```bash
curl -u user1:user1 -X POST http://localhost:8000/api/v1/documents \
     -F name="Analysis 1 Zusammenfassung" \
     -F description="Zusammenfassung aus Vorlesung" \
     -F category=1 \
     -F dtype=1 \
     -F public=true \
     -F license=3 \
     -F document=@zusammenfassung.pdf
```

`dtype`: 1 = Zusammenfassung, 2 = Prüfung, 3 = Software,
4 = Lernhilfe, 5 = Testat.

`license`: 1 = Public Domain,
2 = CC BY 3.0, 3 = CC BY-SA 3.0, 4 = CC BY-NC 3.0,
5 = CC BY-NC-SA 3.0. Exams may not be public.

### Rate a document (1-10)

```bash
curl -u user1:user1 -X POST -d score=9 http://localhost:8000/api/v1/documents/34/rate
```

A user cannot rate their own upload.

### Rate a lecturer

```bash
curl -u user1:user1 -X POST -d "category=d&score=8" \
     http://localhost:8000/api/v1/lecturers/7/rate
```

`category`: `d` = didaktisch, `m` = menschlich, `f` = fachlich.

### Vote on a quote or tipp

```bash
curl -u user1:user1 -X POST -d vote=up http://localhost:8000/api/v1/tipps/5/vote
```

`vote` is `up`, `down` or `remove`.

## Errors

| Status | Meaning |
| --- | --- |
| 400 | Validation error (JSON field errors, or `Validierungsfehler` for rate endpoints) |
| 401 | Missing/invalid credentials (`{"detail": "Anmeldedaten fehlen."}`) |
| 403 | Not allowed — e.g. editing an object you did not create |
| 404 | Not found (also returned for documents you may not see, e.g. non-public ones while anonymous) |
