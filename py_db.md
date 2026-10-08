[DuckDB](<https://duckdb.org/>) is an **embedded analytical SQL database** designed to run inside your application, somewhat like SQLite—but optimized for **OLAP/analytics** rather than transactional workloads.

A **stateless DuckDB implementation in Python** generally means:

- No persistent `.duckdb` database file.
- Each operation starts from a clean database instance.
- Data comes from external sources (Parquet, CSV, Pandas/Polars, APIs, etc.).
- SQL is used for transformation/querying.
- The database disappears when the operation/process ends.

### Simple stateless example

```
import duckdb
import pandas as pd

def analyze(data: pd.DataFrame):
    con = duckdb.connect(":memory:")

    result = con.execute("""
        SELECT
            category,
            COUNT(*) AS count,
            AVG(value) AS avg_value
        FROM data
        GROUP BY category
        ORDER BY count DESC
    """).fetchdf()

    con.close()
    return result
```

Here, `:memory:` creates an **in-memory DuckDB database**. Nothing is persisted to disk.

You can make this even simpler:

```
import duckdb

def analyze(data):
    return duckdb.sql("""
        SELECT category, SUM(amount) AS total
        FROM data
        GROUP BY category
    """).df()
```

DuckDB can query Python objects directly, so you don't necessarily need to insert the data into tables first.

### Stateless with Parquet

One of DuckDB's particularly useful features is querying files directly:

```
import duckdb

def get_sales(path):
    return duckdb.sql(f"""
        SELECT
            customer_id,
            SUM(amount) AS total
        FROM read_parquet('{path}')
        GROUP BY customer_id
    """).df()
```

The Parquet file is your **state**, while DuckDB itself is just the computation engine.

For a truly stateless service, a common architecture is:

```
             ┌─────────────────┐
             │  API / Python   │
             └────────┬────────┘
                      │
                      ▼
             ┌─────────────────┐
             │    DuckDB       │
             │   :memory:      │
             └────────┬────────┘
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Parquet       CSV       DataFrame
       / S3          files      / API
```

Each request can create a fresh DuckDB connection, execute SQL, return the result, and throw the connection away.

### If you need a persistent dataset but stateless compute

This is often the **best design** for a web service:

```
             Stateless Python workers
              ┌──────┬──────┬──────┐
              │      │      │      │
              ▼      ▼      ▼      ▼
            DuckDB DuckDB DuckDB DuckDB
              │      │      │      │
              └──────┼──────┼──────┘
                     ▼
               Object storage
             ┌─────────────────┐
             │ Parquet / S3    │
             └─────────────────┘
```

The workers don't maintain database state. Your durable state lives in **Parquet/object storage**, and DuckDB performs the computation over that data.

This works particularly well for analytical workloads because DuckDB can query Parquet directly and push filters/aggregations down into the file scan.

If by "stateless implementation" you mean **a stateless Python API/service where multiple requests can concurrently query datasets**,  I can show you a production-style implementation with \*\*FastAPI + DuckDB + Parquet/S3\*\* , including connection lifecycle and concurrency considerations.

Yes. The key design is to treat **S3/Parquet as the durable state** and **DuckDB as an ephemeral query engine**. Each FastAPI request gets its own in-memory DuckDB connection, runs a read-only analytical query, and releases the connection afterward.

## Architecture

```
                    ┌──────────────────────┐
                    │       FastAPI        │
                    │      API server      │
                    └──────────┬───────────┘
                               │
                 request      │      request
                    ┌──────────┴──────────┐
                    ▼                     ▼
              DuckDB :memory:       DuckDB :memory:
              ephemeral             ephemeral
                    │                     │
                    └──────────┬──────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    S3 / S3-compatible │
                    │       storage        │
                    │                      │
                    │  sales/*.parquet     │
                    │  customers/*.parquet │
                    └──────────────────────┘
```

There is **no database server** and no local `.duckdb` file.

## 1\. Project structure

```
analytics-api/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── duckdb_service.py
│   └── schemas.py
├── tests/
│   └── test_api.py
├── Dockerfile
├── requirements.txt
└── .env
```

## 2\. Dependencies

```
fastapi
uvicorn[standard]
duckdb
boto3
pydantic-settings
```

For example:

```
pip install fastapi uvicorn duckdb boto3 pydantic-settings
```

## 3\. Configuration

```
# app/config.py

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    aws_region: str = "us-east-1"

    s3_bucket: str

    # Optional if you're using S3-compatible storage such as MinIO.
    s3_endpoint_url: str | None = None

    duckdb_memory_limit: str = "1GB"
    duckdb_threads: int = 2

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

settings = Settings()
```

`.env`:

```
S3_BUCKET=my-analytics-bucket
AWS_REGION=us-east-1

DUCKDB_MEMORY_LIMIT=1GB
DUCKDB_THREADS=2
```

In production, I would normally inject these through your container/orchestrator rather than actually mounting a `.env` file.

---

# 4\. DuckDB service

This is the important part.

```
# app/duckdb_service.py

from contextlib import contextmanager

import duckdb

from .config import settings

@contextmanager
def duckdb_connection():
    """
    Creates an ephemeral DuckDB connection.

    Nothing is persisted locally.
    The connection disappears when the context exits.
    """

    con = duckdb.connect(database=":memory:")

    try:
        con.execute(
            f"SET memory_limit = '{settings.duckdb_memory_limit}'"
        )

        con.execute(
            f"SET threads = {settings.duckdb_threads}"
        )

        # Don't allow accidental writes to a database.
        con.execute("SET preserve_insertion_order = false")

        yield con

    finally:
        con.close()
```

The important line is:

```
duckdb.connect(database=":memory:")
```

Every request can therefore have an isolated database.

---

# 5\. Configure S3 access

DuckDB has an HTTP/S3 filesystem layer through its `httpfs` extension.

A useful production pattern is to configure credentials using environment variables or AWS's normal credential chain.

For example:

```
# app/duckdb_service.py

from contextlib import contextmanager

import duckdb

from .config import settings

@contextmanager
def duckdb_connection():
    con = duckdb.connect(":memory:")

    try:
        con.execute("INSTALL httpfs")
        con.execute("LOAD httpfs")

        con.execute(
            f"SET s3_region = '{settings.aws_region}'"
        )

        if settings.s3_endpoint_url:
            con.execute(
                f"SET s3_endpoint = '{settings.s3_endpoint_url}'"
            )

        con.execute(
            f"SET memory_limit = '{settings.duckdb_memory_limit}'"
        )

        con.execute(
            f"SET threads = {settings.duckdb_threads}"
        )

        yield con

    finally:
        con.close()
```

For AWS, I'd recommend using **IAM roles / task roles / workload identity** rather than putting AWS access keys in your application configuration.

---

# 6\. Define the API schema

```
# app/schemas.py

from datetime import date

from pydantic import BaseModel, Field

class SalesSummary(BaseModel):
    date: date
    revenue: float
    orders: int

class SalesResponse(BaseModel):
    rows: list[SalesSummary]
```

---

# 7\. FastAPI application

```
# app/main.py

from datetime import date

from fastapi import FastAPI, HTTPException, Query

from .config import settings
from .duckdb_service import duckdb_connection
from .schemas import SalesResponse, SalesSummary

app = FastAPI(
    title="Analytics API",
    version="1.0.0",
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/sales", response_model=SalesResponse)
def sales(
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    if end_date < start_date:
        raise HTTPException(
            status_code=400,
            detail="end_date must be >= start_date",
        )

    parquet_path = (
        f"s3://{settings.s3_bucket}/sales/*.parquet"
    )

    query = """
        SELECT
            CAST(order_date AS DATE) AS date,
            SUM(amount) AS revenue,
            COUNT(*) AS orders
        FROM read_parquet(?)
        WHERE order_date >= ?
          AND order_date <= ?
        GROUP BY 1
        ORDER BY 1
    """

    with duckdb_connection() as con:
        result = con.execute(
            query,
            [
                parquet_path,
                start_date,
                end_date,
            ],
        ).fetchall()

    rows = [
        SalesSummary(
            date=row[0],
            revenue=float(row[1]),
            orders=int(row[2]),
        )
        for row in result
    ]

    return SalesResponse(rows=rows)
```

Notice something important:

```
read_parquet(?)
```

and:

```
WHERE order_date >= ?
```

We're **parameterizing values** rather than constructing SQL with user input.

---

# 8\. What happens during a request?

Suppose the client calls:

```
GET /sales?start_date=2026-01-01&end_date=2026-01-31
```

The application effectively does:

```
Request
   │
   ▼
Create DuckDB :memory:
   │
   ▼
Connect to S3
   │
   ▼
Read only relevant Parquet data
   │
   ▼
Aggregate in DuckDB
   │
   ▼
Return JSON
   │
   ▼
Close DuckDB
   │
   ▼
Memory released
```

There is no:

```
sales.db
analytics.db
duckdb.sqlite
```

sitting on the API server.

---

# 9\. Your Parquet layout matters

For production analytics, I'd strongly recommend partitioning the data.

Instead of:

```
s3://bucket/sales.parquet
```

use something like:

```
s3://bucket/sales/
    year=2026/
        month=01/
            data.parquet
        month=02/
            data.parquet
        month=03/
            data.parquet
    year=2027/
        month=01/
            data.parquet
```

Then your query can be:

```
SELECT
    CAST(order_date AS DATE) AS date,
    SUM(amount) AS revenue
FROM read_parquet(
    's3://bucket/sales/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 1
GROUP BY 1;
```

This can dramatically reduce the amount of data that needs to be scanned.

Even better, your files should generally be reasonably sized rather than having millions of tiny Parquet objects.

---

# 10\. Avoid this design

I would **not** do this:

```
# BAD

con = duckdb.connect("analytics.duckdb")

@app.get("/sales")
def sales():
    return con.execute(...)
```

Now you have:

- persistent local state
- shared mutable connection
- concurrency concerns
- local disk dependency
- container restart issues
- potential locking/contention problems

That's the opposite of what you're trying to achieve.

---

# 11\. Don't create a global DuckDB connection

You might be tempted to do:

```
# DON'T

db = duckdb.connect(":memory:")
```

and then:

```
@app.get("/sales")
def sales():
    return db.execute(...)
```

Instead:

```
@app.get("/sales")
def sales():
    with duckdb_connection() as db:
        ...
```

This makes the request boundary explicit.

For an API with many concurrent requests, that isolation is valuable.

---

# 12\. But creating a connection every request—isn't that expensive?

Usually it's perfectly reasonable for an analytical API, particularly if the actual work is scanning/aggregating Parquet in S3.

But there are two different costs:

```
DuckDB connection creation
        ↓
       cheap

S3 network I/O
        ↓
       potentially expensive

Parquet scanning
        ↓
       potentially expensive

Aggregation
        ↓
       potentially expensive
```

The DuckDB connection isn't normally the thing you should optimize first.

If profiling eventually shows connection initialization becoming significant, you can introduce a carefully managed connection/pool strategy—but then you're moving away from the simplest stateless model.

---

# 13\. Production concurrency

There's an important FastAPI detail here.

A synchronous endpoint:

```
@app.get("/sales")
def sales():
    ...
```

is run by FastAPI/Starlette in a threadpool.

That's actually useful because DuckDB queries are CPU-intensive and/or blocking on I/O.

I would **not automatically change it to**:

```
@app.get("/sales")
async def sales():
    ...
```

just because FastAPI supports async.

DuckDB's Python API is synchronous, so an async endpoint can accidentally block the event loop.

For heavier workloads, I'd instead control concurrency at the application/container level.

For example:

```
             Load Balancer
                    │
       ┌────────────┼────────────┐
       ▼            ▼            ▼
   FastAPI #1   FastAPI #2   FastAPI #3
       │            │            │
   DuckDB       DuckDB       DuckDB
    :memory:     :memory:     :memory:
       │            │            │
       └────────────┼────────────┘
                    ▼
                    S3
```

---

# 14\. Control DuckDB's resource usage

This is **very important** in production.

If ten requests arrive and each DuckDB instance can consume unlimited memory and CPU, your container can get killed.

That's why I included:

```
con.execute("SET memory_limit = '1GB'")
con.execute("SET threads = 2")
```

You can tune these according to the container's resources.

For example, if your container has:

```
4 CPU
8 GB RAM
```

you might configure something like:

```
DuckDB memory/request: 1 GB
DuckDB threads/request: 2
Maximum concurrent requests: 3
```

The exact numbers should come from load testing rather than guesswork.

---

# 15\. Query parameters vs SQL injection

Don't do:

```
query = f"""
SELECT *
FROM read_parquet('{user_path}')
WHERE customer_id = '{customer_id}'
"""
```

Instead:

```
query = """
SELECT *
FROM read_parquet(?)
WHERE customer_id = ?
"""

con.execute(
    query,
    [parquet_path, customer_id],
)
```

There is one additional consideration: **SQL identifiers cannot generally be parameterized like values**.

So if you allow a client to choose a dataset, don't blindly do:

```
read_parquet(user_supplied_path)
```

Instead, map allowed logical names to known paths:

```
DATASETS = {
    "sales": "s3://my-bucket/sales/**/*.parquet",
    "customers": "s3://my-bucket/customers/**/*.parquet",
}
```

Then:

```
dataset_path = DATASETS.get(dataset)

if dataset_path is None:
    raise HTTPException(
        status_code=404,
        detail="Unknown dataset",
    )
```

That's much safer.

---

# 16\. A slightly more production-oriented service

I'd actually separate the API from the analytics layer.

```
# app/analytics.py

from datetime import date

from .config import settings
from .duckdb_service import duckdb_connection

def get_sales(
    start_date: date,
    end_date: date,
):
    path = (
        f"s3://{settings.s3_bucket}/sales/**/*.parquet"
    )

    query = """
        SELECT
            CAST(order_date AS DATE) AS date,
            SUM(amount) AS revenue,
            COUNT(*) AS orders
        FROM read_parquet(
            ?,
            hive_partitioning = true
        )
        WHERE order_date >= ?
          AND order_date <= ?
        GROUP BY 1
        ORDER BY 1
    """

    with duckdb_connection() as con:
        return con.execute(
            query,
            [path, start_date, end_date],
        ).fetchall()
```

Then your API becomes thin:

```
# app/main.py

from datetime import date

from fastapi import FastAPI, Query

from .analytics import get_sales

app = FastAPI()

@app.get("/sales")
def sales(
    start_date: date = Query(...),
    end_date: date = Query(...),
):
    rows = get_sales(
        start_date,
        end_date,
    )

    return {
        "rows": [
            {
                "date": row[0],
                "revenue": float(row[1]),
                "orders": int(row[2]),
            }
            for row in rows
        ]
    }
```

Now you can test your analytical functions without involving HTTP.

---

# 17\. Docker

A simple production container:

```
FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD [
    "uvicorn",
    "app.main:app",
    "--host",
    "0.0.0.0",
    "--port",
    "8000"
]
```

I'd generally let your container/orchestrator handle scaling rather than running an enormous number of Uvicorn workers inside one container.

For example:

```
Kubernetes / ECS / Cloud Run
             │
       ┌─────┴─────┐
       ▼           ▼
    container   container
       │           │
    FastAPI     FastAPI
       │           │
    DuckDB      DuckDB
       │           │
       └─────┬─────┘
             ▼
             S3
```

---

# 18\. Authentication to S3

For AWS, avoid:

```
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

inside your source code.

Prefer the platform's identity mechanism:

```
ECS task role
       or
EKS IRSA
       or
EC2 instance role
       or
Lambda execution role
       or
other workload identity
```

Then DuckDB's S3 access can use the AWS credential chain.

This keeps your application stateless **and** avoids managing long-lived credentials.

---

# 19\. Read-only analytical architecture

The architecture I'd recommend for your use case is:

```
                 DATA INGESTION
                       │
                       ▼
              ┌─────────────────┐
              │ S3 / Object     │
              │ Storage         │
              │                 │
              │ Parquet         │
              └────────┬────────┘
                       │
                       │ read
                       ▼
             ┌───────────────────┐
             │   FastAPI         │
             │                   │
             │   request         │
             │      │            │
             │      ▼            │
             │ DuckDB :memory:   │
             │      │            │
             │      ▼            │
             │   SQL query       │
             └────────┬──────────┘
                      │
                      ▼
                    JSON
```

The really nice property is that **there is no database state to synchronize between API instances**.

If you run 100 API containers:

```
API #1 ──┐
API #2 ──┤
API #3 ──┤
API #4 ──┤──────► S3 / Parquet
 ...     │
API #100─┘
```

Every instance sees the same source of truth.

---

## 20\. One important caveat: don't use DuckDB as your primary transactional database

This architecture is excellent for:

- dashboards
- reporting APIs
- analytics
- aggregations
- ETL/ELT
- querying data lakes
- ad-hoc SQL
- large Parquet datasets

It is **not** what I'd choose for:

- thousands of concurrent OLTP transactions
- user/account state
- order processing
- inventory mutations
- transactional writes
- highly concurrent point updates

For those, I'd use something like PostgreSQL as the transactional system and potentially DuckDB as the analytical layer.

---

## The pattern I'd use

If you're building a serious analytics API, I'd settle on this:

```
              ┌───────────────┐
              │    Clients    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │    FastAPI    │
              └───────┬───────┘
                      │
             one ephemeral DB
                      │
                      ▼
              ┌───────────────┐
              │    DuckDB     │
              │   :memory:    │
              │               │
              │ read-only     │
              │ analytical    │
              └───────┬───────┘
                      │
                      ▼
              ┌───────────────┐
              │      S3       │
              │               │
              │ partitioned   │
              │   Parquet     │
              └───────────────┘
```

**S3 is the state. DuckDB is the compute. FastAPI is the interface.**

That separation gives you a genuinely stateless API layer, easy horizontal scaling, and no database server to operate.

Exactly. In that case, I would change the architecture slightly from the previous example.

You want a **two-stage system**:

```
                    ┌──────────────────┐
                    │     Snowflake    │
                    │  source of truth │
                    └────────┬─────────┘
                             │
                       scheduled job
                             │
                             ▼
                    ┌──────────────────┐
                    │  Extract/Export  │
                    │     service      │
                    └────────┬─────────┘
                             │
                       Parquet files
                             │
                             ▼
              ┌─────────────────────────────┐
              │        Blob Storage         │
              │                             │
              │ S3 / Azure Blob / GCS       │
              │                             │
              │ sales/                      │
              │   date=2026-10-01/*.parquet│
              │   date=2026-10-02/*.parquet│
              └──────────────┬──────────────┘
                             │
                             │ read
                             ▼
                    ┌──────────────────┐
                    │     FastAPI      │
                    │                  │
                    │ DuckDB :memory: │
                    └──────────────────┘
```

This gives you a very clean separation:

- **Snowflake** = source of truth
- **Blob storage** = durable analytical cache/data lake
- **Parquet** = storage format
- **DuckDB** = query engine
- **FastAPI** = API
- **No persistent database in FastAPI**

Snowflake's Python connector supports fetching results as Arrow/Pandas batches, which is useful for large exports.  Snowflake Docs+1  DuckDB can also directly read and write Parquet on S3-compatible storage.  DuckDB+1

## The important question: how much data?

The implementation depends heavily on whether you're extracting:

- 10,000 rows
- 10 million rows
- 500 million rows
- several TB

For anything beyond relatively small datasets, **don't do****`fetch_pandas_all()`****and hold the entire Snowflake result in RAM**.

Instead, use Snowflake's batch/Arrow APIs and write batches to Parquet. Snowflake specifically provides `fetch_pandas_batches()` and `fetch_arrow_batches()` for this pattern.  Snowflake Docs+1

---

# 1\. Recommended production architecture

I'd actually have a separate ingestion worker:

```
                    Scheduler
                       │
                       │ every hour/day
                       ▼
                ┌───────────────┐
                │ Extract Worker │
                └───────┬───────┘
                        │
                        │ SQL
                        ▼
                  ┌───────────┐
                  │ Snowflake │
                  └─────┬─────┘
                        │
                   Arrow batches
                        │
                        ▼
              ┌───────────────────┐
              │ Parquet writer    │
              └─────────┬─────────┘
                        │
                        ▼
                ┌──────────────┐
                │ Blob Storage  │
                │              │
                │ Parquet      │
                └──────┬───────┘
                       │
                       │
          ┌────────────┴────────────┐
          ▼                         ▼
     FastAPI #1                 FastAPI #2
          │                         │
       DuckDB                    DuckDB
       :memory:                 :memory:
          │                         │
          └────────────┬────────────┘
                       ▼
                 API response
```

**Do not make the FastAPI request itself fetch from Snowflake.**

That's the biggest architectural recommendation I'd make.

Instead:

```
Snowflake → scheduled ingestion → Blob
                                      ↓
                               FastAPI/DuckDB
```

This means your API remains fast and stateless.

---

# 2\. Snowflake extraction

For example, suppose Snowflake contains:

```
ANALYTICS.SALES
```

with:

```
ORDER_ID
CUSTOMER_ID
ORDER_DATE
AMOUNT
STATUS
```

Your extraction SQL could be:

```
SELECT
    ORDER_ID,
    CUSTOMER_ID,
    ORDER_DATE,
    AMOUNT,
    STATUS
FROM ANALYTICS.SALES
WHERE ORDER_DATE >= ?
  AND ORDER_DATE < ?
```

The incremental boundary is important.

Don't repeatedly download your entire Snowflake table.

Instead:

```
First run:
Snowflake → 2026-01-01 through 2026-10-01

Next run:
Snowflake → 2026-10-01 through 2026-10-02

Next:
Snowflake → 2026-10-02 through 2026-10-03
```

---

# 3\. Python Snowflake extractor

Install:

```
pip install "snowflake-connector-python[pandas]" pyarrow duckdb boto3
```

Snowflake documents the Pandas-compatible connector and its batch APIs.  Snowflake Docs

A simple extractor:

```
import snowflake.connector

def extract_sales(start_date, end_date):

    conn = snowflake.connector.connect(
        account="...",
        user="...",
        password="...",
        warehouse="ANALYTICS_WH",
        database="ANALYTICS",
        schema="PUBLIC",
    )

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                ORDER_ID,
                CUSTOMER_ID,
                ORDER_DATE,
                AMOUNT,
                STATUS
            FROM SALES
            WHERE ORDER_DATE >= %s
              AND ORDER_DATE < %s
            """,
            (start_date, end_date),
        )

        for batch in cursor.fetch_arrow_batches():
            yield batch

    finally:
        conn.close()
```

The important part is:

```
for batch in cursor.fetch_arrow_batches():
```

rather than:

```
df = cursor.fetch_pandas_all()
```

The first approach lets you process the result incrementally.

---

# 4\. Convert Arrow → Parquet

Each batch can be written to Parquet.

For example:

```
import pyarrow.parquet as pq

def write_batch(batch, path):
    pq.write_table(
        batch,
        path,
        compression="zstd",
    )
```

But in production, I wouldn't write the final Parquet directly to the blob location while the extraction is still running.

Instead:

```
Snowflake
    ↓
temporary Parquet
    ↓
validate
    ↓
upload
    ↓
mark successful
```

That prevents consumers from seeing a partially written dataset.

---

# 5\. If you're using AWS S3

There are actually two good approaches.

### Option A — Python writes Parquet to S3

```
Snowflake
    ↓
Arrow
    ↓
PyArrow
    ↓
S3
```

### Option B — DuckDB does the Parquet export

```
Snowflake
    ↓
Arrow
    ↓
DuckDB
    ↓
COPY ... TO s3://...
```

DuckDB supports `COPY ... TO 's3://...'` for Parquet and also supports partitioned exports.  DuckDB+1

For your architecture, **I prefer Option A for ingestion and DuckDB for querying**.

You don't really need DuckDB in the Snowflake extraction path.

---

# 6\. S3 layout

Don't put everything into one giant file.

I'd use something like:

```
s3://my-company-analytics/
    sales/
        year=2026/
            month=10/
                day=01/
                    part-000.parquet
                    part-001.parquet

                day=02/
                    part-000.parquet
                    part-001.parquet

                day=03/
                    part-000.parquet
```

This is **Hive partitioning**.

DuckDB understands this structure and can query the Parquet files directly.  DuckDB

Then:

```
SELECT
    customer_id,
    SUM(amount)
FROM read_parquet(
    's3://my-company-analytics/sales/**/*.parquet',
    hive_partitioning = true
)
WHERE year = 2026
  AND month = 10
  AND day = 3
GROUP BY customer_id;
```

DuckDB can also perform partial reads from Parquet rather than downloading an entire file, which is one of the reasons this architecture works well.  DuckDB

---

# 7\. Even better: incremental ingestion

I'd maintain a small metadata record somewhere:

```
dataset: sales
last_successful_date: 2026-10-06
last_successful_run: 2026-10-07T02:00:00Z
status: success
```

Then your ingestion job does:

```
last_date = get_last_successful_date()

start = last_date
end = today()

extract_snowflake(start, end)
write_parquet(start, end)
validate()
mark_success(end)
```

This gives you:

```
                 ┌──────────────┐
                 │ ingestion    │
                 │ metadata     │
                 └──────┬───────┘
                        │
                        ▼
Snowflake ────────► Parquet ────────► Blob
```

The metadata itself can be stored in something lightweight such as DynamoDB, Postgres, or your cloud's metadata service.

---

# 8\. Your FastAPI side becomes extremely simple

Once the Parquet files exist, FastAPI doesn't care about Snowflake.

For example:

```
import duckdb

def query_sales(start_date, end_date):

    con = duckdb.connect(":memory:")

    try:
        con.execute("INSTALL httpfs")
        con.execute("LOAD httpfs")

        result = con.execute(
            """
            SELECT
                customer_id,
                SUM(amount) AS revenue,
                COUNT(*) AS orders
            FROM read_parquet(
                's3://my-company-analytics/sales/**/*.parquet',
                hive_partitioning = true
            )
            WHERE order_date >= ?
              AND order_date < ?
            GROUP BY customer_id
            ORDER BY revenue DESC
            """,
            [start_date, end_date],
        ).fetchall()

        return result

    finally:
        con.close()
```

DuckDB's `httpfs` extension supports reading Parquet directly from S3 and other S3-compatible storage.  DuckDB+1

---

# 9\. Authentication

This is another place I'd make the architecture clean.

### Snowflake

Use:

```
Snowflake key-pair authentication
```

or your organization's preferred workload identity.

Avoid:

```
password="hardcoded-password"
```

### Blob storage

For AWS, prefer:

```
IAM Role
   ↓
FastAPI / ingestion worker
   ↓
S3
```

DuckDB supports an AWS credential chain for S3 access, so you don't have to hardcode access keys.  DuckDB

For Azure Blob Storage, the implementation is slightly different; if your "blob storage" means **Azure Blob Storage**, I'd use Azure's identity/SDK layer rather than assuming S3.

---

# 10\. One thing I'd change if you're on Azure

If your environment is:

```
Snowflake
   ↓
Azure Blob Storage
   ↓
FastAPI
   ↓
DuckDB
```

then tell me that explicitly, because I'd design the storage layer differently.

The architecture remains:

```
Snowflake
    │
    ▼
Ingestion Worker
    │
    ▼
Azure Blob Storage
    │
    │ Parquet
    ▼
DuckDB
    │
    ▼
FastAPI
```

But the authentication and filesystem integration are different from AWS S3.

---

# 11\. The complete production flow

I'd implement it approximately like this:

```
                    ┌─────────────────┐
                    │    Scheduler    │
                    │  hourly / daily │
                    └────────┬────────┘
                             │
                             ▼
                    ┌─────────────────┐
                    │ Ingestion Job   │
                    │                 │
                    │ Python          │
                    │ Snowflake SDK   │
                    │ PyArrow         │
                    └────────┬────────┘
                             │
                             │ incremental SQL
                             ▼
                    ┌─────────────────┐
                    │    Snowflake    │
                    └────────┬────────┘
                             │
                        Arrow batches
                             │
                             ▼
                    ┌─────────────────┐
                    │    Parquet      │
                    │    writer       │
                    └────────┬────────┘
                             │
                             ▼
                 ┌───────────────────────┐
                 │      Blob Storage     │
                 │                       │
                 │ sales/                │
                 │ year=2026/            │
                 │ month=10/             │
                 │ day=07/*.parquet      │
                 └───────────┬───────────┘
                             │
                             │
                   ┌─────────┴─────────┐
                   │                   │
                   ▼                   ▼
              FastAPI #1          FastAPI #2
                   │                   │
              DuckDB :memory:     DuckDB :memory:
                   │                   │
                   └─────────┬─────────┘
                             ▼
                          Client
```

### The key design principle

**Don't think of DuckDB as your database.**

Think of it as:

> "A temporary SQL compute engine that reads my durable Parquet data."

That distinction makes the architecture much easier to scale.

---

## What I would build for you

If this is a real project rather than a toy example, I'd build these four components:

```
1. ingestion/
   snowflake → parquet → blob

2. metadata/
   tracks successful ingestion windows

3. analytics/
   DuckDB queries over Parquet

4. api/
   FastAPI endpoints
```

And the ingestion would support:

- incremental loads
- batch fetching from Snowflake
- Parquet compression
- Hive partitioning
- retries
- idempotency
- atomic publishing
- schema validation
- ingestion metadata
- logging/metrics
- cloud IAM rather than embedded credentials

**If you tell me whether your blob storage is AWS S3, Azure Blob Storage, or GCP Cloud Storage, and roughly how large the Snowflake dataset is (e.g. 10 GB, 500 GB, 5 TB), I can give you the complete production code for the Snowflake → Parquet → blob → DuckDB → FastAPI pipeline.**


Absolutely. A **portfolio analytics** use case makes the architecture much clearer because we can separate the **authoritative financial data** from the **read-optimized analytics layer**.

I would model it like this:

```
                    ┌─────────────────────┐
                    │      Snowflake      │
                    │                     │
                    │ Portfolio holdings  │
                    │ Transactions        │
                    │ Security master     │
                    │ Prices / FX         │
                    └──────────┬──────────┘
                               │
                         scheduled ETL
                               │
                               ▼
                    ┌─────────────────────┐
                    │  Parquet Generator  │
                    │                     │
                    │ Python + PyArrow    │
                    └──────────┬──────────┘
                               │
                               ▼
                 ┌────────────────────────────┐
                 │       Blob Storage         │
                 │                            │
                 │ portfolio/                 │
                 │   client=123/              │
                 │     date=2026-10-07/       │
                 │       holdings.parquet     │
                 └─────────────┬──────────────┘
                               │
                               │ read
                               ▼
                    ┌─────────────────────┐
                    │       FastAPI       │
                    │                     │
                    │ DuckDB :memory:    │
                    └──────────┬──────────┘
                               │
                               ▼
                         Client UI/API
```

The important idea is:

> **Snowflake owns the financial truth. Parquet is the analytical snapshot. DuckDB computes the portfolio view.**

## A concrete client experience

Suppose client `ACME-001` logs into your application.

They might see:

```
Portfolio
────────────────────────────────────

Total value              $12,450,320
Today's change              +$42,180
YTD return                    +8.42%

Asset Allocation

Equities                    62.4%
Fixed Income                27.8%
Cash                         6.2%
Alternatives                 3.6%

Top Holdings

Apple Inc.                 $1.24M
Microsoft                  $1.08M
US Treasury 4.25%           $820K
NVIDIA                      $710K
Amazon                      $640K
```

And the API behind that could be:

```
GET /v1/clients/ACME-001/portfolio
```

---

# 1\. Start with the financial data model

I'd assume Snowflake has something like:

### `CLIENT`

```
client_id
client_name
base_currency
```

### `ACCOUNT`

```
account_id
client_id
account_type
currency
```

### `POSITION`

```
account_id
security_id
quantity
as_of_date
```

### `SECURITY`

```
security_id
ticker
name
asset_class
sector
currency
```

### `PRICE`

```
security_id
price_date
price
currency
```

### `FX_RATE`

```
from_currency
to_currency
rate_date
rate
```

### `TRANSACTION`

```
transaction_id
account_id
security_id
transaction_date
transaction_type
quantity
price
amount
currency
```

That is the **source-of-truth model**.

You don't necessarily want to expose this model directly through your API.

---

# 2\. Create an analytical portfolio snapshot

This is where I would introduce an important concept:

## `portfolio_position`

Instead of making DuckDB join six massive tables every time a client opens their portfolio, the ingestion process can produce a denormalized analytical dataset.

For example:

```
client_id
account_id
as_of_date

security_id
ticker
security_name

asset_class
sector

quantity
price
market_value

security_currency
base_currency
fx_rate
market_value_base

weight
```

Example:

```
client_id | ticker | asset_class | quantity | price | market_value
-------------------------------------------------------------------
ACME-001  | AAPL   | Equity      | 5000     | 245   | 1,225,000
ACME-001  | MSFT   | Equity      | 3000     | 360   | 1,080,000
ACME-001  | TLT    | FixedIncome | 5000     | 82    |   410,000
```

This becomes your **portfolio analytics layer**.

---

# 3\. Partition the Parquet data

I'd store it something like:

```
portfolio/
    positions/
        as_of_date=2026-10-01/
            part-000.parquet

        as_of_date=2026-10-02/
            part-000.parquet

        as_of_date=2026-10-03/
            part-000.parquet

        ...

        as_of_date=2026-10-07/
            part-000.parquet
```

If there are many clients:

```
portfolio/
    positions/
        as_of_date=2026-10-07/
            part-000.parquet
            part-001.parquet
            part-002.parquet
```

You **don't necessarily want one file per client**.

For a large client population, that can create millions of tiny files.

Instead, let Parquet contain many clients and partition primarily by a useful query dimension such as `as_of_date`.

---

# 4\. The ingestion process

Every night—or hourly, depending on your requirements:

```
                 Snowflake
                     │
                     │
             ┌───────▼────────┐
             │ Portfolio ETL  │
             └───────┬────────┘
                     │
                     ▼
             Join / calculate
                     │
                     ▼
                 PyArrow
                     │
                     ▼
                 Parquet
                     │
                     ▼
               Blob Storage
```

The SQL might look approximately like:

```
SELECT
    p.client_id,
    p.account_id,
    p.security_id,

    p.as_of_date,

    s.ticker,
    s.name AS security_name,
    s.asset_class,
    s.sector,

    p.quantity,
    px.price,

    p.quantity * px.price AS market_value,

    p.currency AS security_currency,
    c.base_currency,

    fx.rate AS fx_rate,

    p.quantity
        * px.price
        * fx.rate AS market_value_base

FROM positions p

JOIN security s
    ON p.security_id = s.security_id

JOIN prices px
    ON p.security_id = px.security_id
    AND p.as_of_date = px.price_date

JOIN client c
    ON p.client_id = c.client_id

JOIN fx_rates fx
    ON px.currency = fx.from_currency
    AND c.base_currency = fx.to_currency
    AND p.as_of_date = fx.rate_date

WHERE p.as_of_date = ?
```

Now your Parquet dataset already contains the information required for most portfolio screens.

---

# 5\. Why this is better than querying Snowflake directly

Imagine 10,000 clients open the application around 9 AM.

If every request does:

```
FastAPI
   ↓
Snowflake
   ↓
JOIN positions
JOIN securities
JOIN prices
JOIN FX
   ↓
calculate portfolio
```

you're using Snowflake as your application serving layer.

That's expensive and introduces latency.

Instead:

```
                    Snowflake
                       │
                   once/hour
                       │
                       ▼
                    Parquet
                       │
        ┌──────────────┼──────────────┐
        ▼              ▼              ▼
     Client A       Client B       Client C
     DuckDB         DuckDB         DuckDB
```

Now your API is doing relatively cheap analytical reads.

---

# 6\. FastAPI endpoint

The API can be extremely simple.

```
from fastapi import FastAPI, HTTPException
import duckdb

app = FastAPI()

PORTFOLIO_PATH = (
    "s3://my-bucket/portfolio/positions/**/*.parquet"
)

@app.get("/v1/clients/{client_id}/portfolio")
def get_portfolio(client_id: str):

    con = duckdb.connect(":memory:")

    try:
        result = con.execute(
            """
            SELECT
                ticker,
                security_name,
                asset_class,
                sector,
                quantity,
                price,
                market_value_base
            FROM read_parquet(
                ?,
                hive_partitioning = true
            )
            WHERE client_id = ?
              AND as_of_date = (
                  SELECT MAX(as_of_date)
                  FROM read_parquet(
                      ?,
                      hive_partitioning = true
                  )
                  WHERE client_id = ?
              )
            ORDER BY market_value_base DESC
            """,
            [
                PORTFOLIO_PATH,
                client_id,
                PORTFOLIO_PATH,
                client_id,
            ],
        ).fetchall()

        return {
            "client_id": client_id,
            "positions": [
                {
                    "ticker": row[0],
                    "name": row[1],
                    "asset_class": row[2],
                    "sector": row[3],
                    "quantity": row[4],
                    "price": row[5],
                    "market_value": row[6],
                }
                for row in result
            ],
        }

    finally:
        con.close()
```

Although this works, I'd improve it further by making the **latest available portfolio date a metadata concept**, rather than discovering it with a full scan on every request.

---

# 7\. Add a portfolio snapshot manifest

This is a very useful production pattern.

Have a small metadata record:

```
{
  "dataset": "portfolio_positions",
  "as_of_date": "2026-10-07",
  "status": "published",
  "published_at": "2026-10-07T06:30:00Z"
}
```

Then your API knows:

```
Current portfolio snapshot
        ↓
2026-10-07
```

and reads only:

```
portfolio/
  positions/
    as_of_date=2026-10-07/
```

This is much more efficient.

---

# 8\. Then your query becomes beautiful

```
def get_portfolio(client_id: str, as_of_date: str):

    con = duckdb.connect(":memory:")

    try:
        return con.execute(
            """
            SELECT
                ticker,
                security_name,
                asset_class,
                sector,
                quantity,
                price,
                market_value_base
            FROM read_parquet(
                ?
            )
            WHERE client_id = ?
            ORDER BY market_value_base DESC
            """,
            [
                f"s3://my-bucket/portfolio/"
                f"positions/as_of_date={as_of_date}/*.parquet",
                client_id,
            ],
        ).fetchdf()

    finally:
        con.close()
```

The API only scans the relevant day's data.

---

# 9\. Portfolio summary becomes SQL

You can expose multiple endpoints.

### Total portfolio

```
SELECT
    SUM(market_value_base) AS portfolio_value
FROM read_parquet(?)
WHERE client_id = ?
```

### Asset allocation

```
SELECT
    asset_class,
    SUM(market_value_base) AS value,
    SUM(market_value_base)
        / SUM(SUM(market_value_base))
          OVER () AS weight
FROM read_parquet(?)
WHERE client_id = ?
GROUP BY asset_class
ORDER BY value DESC
```

Result:

```
Equity          $7.76M    62.4%
Fixed Income    $3.46M    27.8%
Cash            $0.77M     6.2%
Alternatives    $0.45M     3.6%
```

### Sector allocation

```
SELECT
    sector,
    SUM(market_value_base) AS value
FROM read_parquet(?)
WHERE client_id = ?
  AND asset_class = 'Equity'
GROUP BY sector
ORDER BY value DESC
```

### Top holdings

```
SELECT
    ticker,
    security_name,
    SUM(market_value_base) AS value
FROM read_parquet(?)
WHERE client_id = ?
GROUP BY ticker, security_name
ORDER BY value DESC
LIMIT 10
```

---

# 10\. Performance becomes interesting here

Suppose you have:

```
10,000 clients
5,000 securities
2 years of daily positions
```

That's potentially:

```
10,000 × 5,000 × ~500 trading days
```

which is a **very large analytical dataset**.

You don't want to create:

```
10,000 clients × 500 dates
```

individual files.

Instead, use reasonably sized Parquet files:

```
portfolio/
    positions/
        as_of_date=2026-10-07/
            part-000.parquet
            part-001.parquet
            ...
```

DuckDB can then filter:

```
WHERE client_id = ?
```

and Parquet's columnar format allows it to avoid reading unnecessary columns.

---

# 11\. Security is especially important here

This is a financial application, so I'd put authorization **in front of the DuckDB query**.

Don't trust:

```
GET /clients/ABC/portfolio
```

to mean the user is allowed to see `ABC`.

Instead:

```
JWT
 │
 ▼
Authentication
 │
 ▼
Authorization
 │
 ├── user_id
 ├── organization_id
 └── allowed_client_ids
          │
          ▼
       DuckDB
```

For example:

```
@app.get("/v1/clients/{client_id}/portfolio")
def get_portfolio(
    client_id: str,
    user=Depends(get_current_user),
):

    if not user.can_access_client(client_id):
        raise HTTPException(
            status_code=403,
            detail="Forbidden",
        )

    ...
```

Then use the authorized `client_id` as a parameter.

**Never allow the client to provide arbitrary S3 paths.**

---

# 12\. I would also separate "position" from "performance"

This is important for a real portfolio application.

Your first dataset might be:

```
portfolio_positions
```

which answers:

> "What do I own right now?"

But eventually you'll want:

```
portfolio_daily_values
```

for:

> "How has my portfolio performed?"

For example:

```
date
client_id
portfolio_value
cash_value
equity_value
bond_value
```

Then you can calculate:

```
              Portfolio value
                    │
                    ▼
2026-01-01 ───── $10.0M
2026-02-01 ───── $10.4M
2026-03-01 ───── $10.2M
2026-04-01 ───── $10.8M
...
```

And your API can provide:

```
GET /v1/clients/{id}/portfolio/performance
```

---

# 13\. Eventually you get a very nice analytical model

I'd probably have these Parquet datasets:

```
portfolio/
│
├── positions/
│   └── as_of_date=YYYY-MM-DD/
│       └── *.parquet
│
├── portfolio_values/
│   └── date=YYYY-MM-DD/
│       └── *.parquet
│
├── transactions/
│   └── year=YYYY/
│       └── month=MM/
│           └── *.parquet
│
└── performance/
    └── date=YYYY-MM-DD/
        └── *.parquet
```

Then DuckDB becomes your **portfolio analytics engine**.

---

# 14\. One distinction I would make

I would **not** put every calculation into the ingestion process.

There are two types of calculations:

### Precompute during ingestion

Good candidates:

- market value
- FX-converted value
- asset class
- sector
- security metadata
- portfolio weights

### Calculate at query time

Good candidates:

- top 10 holdings
- asset allocation
- sector allocation
- portfolio totals
- filters
- grouping
- client-specific views

This gives you:

```
Snowflake
   │
   │ expensive joins / enrichment
   ▼
Parquet
   │
   │ cheap aggregation/filtering
   ▼
DuckDB
   │
   ▼
FastAPI
```

That's a very good division of responsibilities.

---

## The architecture I'd recommend

For the financial use case, I'd settle on:

```
                    ┌──────────────────────┐
                    │      SNOWFLAKE       │
                    │                      │
                    │ Source of truth      │
                    │ Positions            │
                    │ Transactions         │
                    │ Prices               │
                    │ FX                   │
                    └──────────┬───────────┘
                               │
                        Scheduled ETL
                               │
                               ▼
                    ┌──────────────────────┐
                    │   PYTHON INGESTION   │
                    │                      │
                    │ Snowflake connector  │
                    │ PyArrow              │
                    │ Validation           │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │    BLOB STORAGE      │
                    │                      │
                    │     PARQUET          │
                    │                      │
                    │ positions            │
                    │ values               │
                    │ performance          │
                    │ transactions         │
                    └──────────┬───────────┘
                               │
                         read-only
                               │
                               ▼
                    ┌──────────────────────┐
                    │       FASTAPI        │
                    │                      │
                    │ Authentication       │
                    │ Authorization        │
                    │ API                  │
                    └──────────┬───────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │       DUCKDB        │
                    │                      │
                    │    :memory:          │
                    │                      │
                    │ Portfolio analytics  │
                    └──────────┬───────────┘
                               │
                               ▼
                       Client application
```

The **next step I'd recommend** is to build one complete vertical slice rather than designing everything at once:

> **Snowflake****`POSITIONS`****→ daily Parquet snapshot → blob storage →****`GET /clients/{id}/portfolio`****→ DuckDB → portfolio JSON**

Once that works, we can add **portfolio performance, asset allocation, top holdings, historical dates, and transactions** around the same foundation.
