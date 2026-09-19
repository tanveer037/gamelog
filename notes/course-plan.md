# Course plan — Mosh's Django series, applied to gamelog

Skipping the course's own projects (cart, orders). Building the equivalent here.

```
[x]  applied in gamelog
[~]  covered in conversation, never written
[ ]  not touched
```

---

# Part 1

## 1. Getting Started

- [x] Introduction / Prerequisites / How to Take this Course

## 2. Django Fundamentals

- [x] What is Django · How the Web Works
- [x] Setting Up the Development Environment
- [x] Creating Your First Django Project
- [x] Using the Integrated Terminal in VSCode
- [x] Creating Your First App
- [x] Writing Views
- [x] Mapping URLs to Views
- [ ] Using Templates — *skipped, API-only project*
- [ ] Debugging Django Applications in VSCode
- [x] Using Django Debug Toolbar

## 3. Building a Data Model

- [x] Introduction to Data Modeling
- [x] Building a Data Model — *Game, Platform, Genre, GameSession, JournalEntry*
- [x] Organizing Models in Apps
- [x] Creating Models
- [x] Choice Fields — *`Status(TextChoices)`*
- [ ] Defining One-to-one Relationships
- [x] Defining a One-to-many Relationship — *Game→Platform, Session→Game, Journal→Game*
- [x] Defining Many-to-many Relationships — *Game↔Genre*
- [~] Resolving Circular Relationships
- [~] Generic Relationships

## 4. Setting Up the Database

- [x] Supported Database Engines
- [x] Creating Migrations
- [x] Running Migrations
- [x] Customizing Database Schema — *`Meta.ordering`*
- [~] Reverting Migrations
- [x] Installing MySQL — *and the 8.0 → 8.4 upgrade*
- [x] Connecting to MySQL
- [x] Using MySQL in Django — *plus `.env` / dotenv*
- [ ] Running Custom SQL
- [ ] Generating Dummy Data

## 5. Django ORM

- [x] Managers and QuerySets
- [x] Retrieving Objects
- [x] Filtering Objects
- [~] Complex Lookups Using Q Objects
- [x] Referencing Fields using F Objects — *in `with_hours()`*
- [x] Sorting
- [~] Limiting Results
- [~] Selecting Fields to Query
- [~] Deferring Fields
- [x] Selecting Related Objects — *`select_related` / `prefetch_related`, the N+1 work*
- [~] Aggregating Objects
- [x] Annotating Objects — *`total_playtime`*
- [x] Calling Database Functions — *`Coalesce`*
- [~] Grouping Data
- [~] Working with Expression Wrappers
- [ ] Querying Generic Relationships
- [x] Custom Managers — *`GameQuerySet.as_manager()`*
- [~] Understanding QuerySet Cache
- [x] Creating Objects
- [x] Updating Objects
- [x] Deleting Objects
- [ ] Transactions — *on the checklist, still unused*
- [ ] Executing Raw SQL Queries

## 6. The Admin Site

- [x] Setting Up the Admin Site
- [x] Registering Models
- [x] Customizing the List Page — *`list_display`, `list_editable`, `list_display_links`*
- [x] Adding Computed Columns — *`@admin.display(ordering=...)`*
- [x] Selecting Related Objects — *`list_select_related`*
- [x] Overriding the Base QuerySet — *`get_queryset()` + `with_hours()`*
- [ ] Providing Links to Other Pages
- [x] Adding Search to the List Page
- [x] Adding Filtering to the List Page
- [ ] Creating Custom Actions
- [ ] Customizing Forms
- [ ] Adding Data Validation
- [ ] Editing Children Using Inlines — *sessions/journal inside a game would suit this*
- [ ] Using Generic Relations
- [ ] Extending Pluggable Apps

---

# Part 2

## 2. Building RESTful APIs

- [x] What are RESTful APIs · Resources · Resource Representations · HTTP Methods
- [x] Installing Django REST Framework
- [x] Creating API Views
- [x] Creating Serializers
- [x] Serializing Objects
- [x] Creating Custom Serializer Fields — *`source=`*
- [x] Serializing Relationships — *`source='game.title'`*
- [x] Model Serializers
- [x] Deserializing Objects
- [x] Data Validation
- [x] Saving Objects
- [x] Deleting Objects

## 3. Advanced API Concepts

- [x] Class-based Views
- [x] Mixins
- [x] Generic Views
- [x] Customizing Generic Views — *`perform_create` / `perform_update`*
- [x] ViewSets
- [x] Routers
- [x] Nested Routers — *`/games/<pk>/sessions/`, `/games/<pk>/journal/`*
- [x] Filtering — *hand-written, then deleted*
- [x] Generic Filtering — *`DjangoFilterBackend`, `GameFilter`*
- [x] Searching — *`SearchFilter` on title*
- [x] Sorting — *`OrderingFilter`, including the annotation*
- [x] Pagination — *`PageNumberPagination`, `PAGE_SIZE` 10*

---

# ▶ NEXT — Part 3, Section 5: Automated Testing (45m)

Out of order, deliberately. No dependency on cart, orders or auth.

- [ ] What is Automated Testing
- [ ] Test Behaviours, Not Implementations
- [ ] Tooling — *installs `pytest` + `pytest-django`*
- [ ] Your First Test
- [ ] Running Tests
- [ ] Skipping Tests
- [ ] Continuous Testing
- [ ] Running and Debugging Tests in VSCode
- [ ] Authenticating the User — *needs auth; watch for the idea, revisit later*
- [ ] Single or Multiple Assertions
- [ ] Fixtures
- [ ] Creating Model Instances — *likely `model_bakery`*

**Build:** `GET /tracker/games/` returns 200 · POST valid → 201 · POST invalid → 400 with
the right error keys · `assertNumQueries` on the games list to lock in the N+1 fix.

**Why now:** the last two bugs — generic `create` losing the annotation, and the stale
annotation on PATCH — would both have failed a test before reaching a browser.

---

# Part 2, continued

## 5. Django Authentication System

**Decide before lesson 3:** swapping `AUTH_USER_MODEL` after migrations exist is
officially difficult. Either dump the data, drop the database, swap, re-migrate — or
skip the custom user model and use the default `User`.

- [ ] Django Authentication System
- [ ] Customizing the User Model
- [ ] Extending the User Model
- [ ] Creating User Profiles
- [ ] Groups and Permissions
- [ ] Creating Custom Permissions

## 6. Securing APIs

- [ ] Token-based Authentication
- [ ] Adding the Authentication Endpoints
- [ ] Registering Users
- [ ] Building the Profile API
- [ ] Logging In
- [ ] Inspecting a JSON Web Token
- [ ] Refreshing Tokens
- [ ] Getting the Current User
- [ ] Getting Current User's Profile
- [ ] Applying Permissions
- [ ] Applying Custom Permissions
- [ ] Applying Model Permissions
- [ ] Applying Custom Model Permissions

**Build:** JWT via `djangorestframework-simplejwt` · a `user` FK on `Game` ·
`IsAuthenticated` on writes · a custom permission so you only edit your own games ·
`get_queryset()` filtered by `self.request.user`.

That last one is finally a queryset that depends on the *request user* rather than a
URL kwarg — the other half of why `get_queryset()` is a method.

## Techniques buried in the project sections

Sections 4 and 7 are cart and order builds. Skip them, but four techniques live inside
and appear nowhere else:

- [ ] Serializer-level `create()` with custom logic — *§4, "Adding a Cart Item"*
- [ ] `get_serializer_class()` per action — *§4, "Updating a Cart Item"*
- [ ] `transaction.atomic` — *§7, "Creating an Order"*
- [ ] Signals and custom signals — *§7, lessons 11–12*

**Build (signals):** set `last_played` on `Game` whenever a `GameSession` is saved.

---

# Part 3 — the rest

## 2. Uploading Files (37m)
- [ ] Managing Media Files · Adding Images · Upload API · Validating Uploads · CORS

**Build:** cover art on `Game`.

## 3. Sending Emails (17m)
- [ ] Fake SMTP · Email Backend · Sending · Attachments · Templated Emails

**Build:** skim, or a weekly playtime digest.

## 4. Running Background Tasks (25m)
- [ ] Celery · Message Brokers · Redis · Celery on Windows · Tasks · Periodic Tasks · Monitoring

**Build: the Steam sync.** Poll `playtime_forever`, log the *delta* as a session.
Revisit the double-counting design first — deltas, not totals.

## 6. Performance Testing (35m)
- [ ] Locust · Test Scripts · Optimization Techniques · Profiling with Silk · Verifying Optimizations

**Build:** profile the games endpoint. The formal version of the debug-toolbar work.

## 7. Caching (22m)
- [ ] What is Caching · Backends · Redis · Low-level Cache API · Caching Views

**Build:** cache `total_playtime`.

## 8. Preparing for Production (30m)
- [ ] Static Assets · Logging · Dev/Prod Settings · Gunicorn

## 9. Deployment (37m)
- [ ] Hosting · Git · Procfile · Env Vars · MySQL · Redis · SMTP · Deploying · Docker

**Note:** Heroku's free tier is gone. Concepts hold — Procfile, gunicorn, static files,
environment variables — but you'll be on Railway, Render or Fly.io.

---

# Order

1. ~~Part 2 §3 lessons 8–14~~ ✅
2. **Part 3 §5 — Automated Testing** ← you are here
3. Part 2 §5–6 — Authentication
4. The four buried techniques — serializer `create()`, `get_serializer_class`,
   `transaction.atomic`, signals
5. Part 3 §2, 4, 6, 7, 8, 9

---

# The rule that makes skipping safe

Skipping the course projects only works because you're building your own. Watch for
**recognition**, then apply it here for **capability**. A technique you've only watched
is one you can find again, not one you can use.
