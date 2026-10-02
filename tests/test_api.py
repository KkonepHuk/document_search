import asyncio
from datetime import datetime

import httpx

from app.database import get_elasticsearch, get_session
from app.main import app
from app.models import Document


class FakeScalarResult:
    def __init__(self, value=None):
        self.value = value

    def scalar(self):
        return self.value


class FakeQueryResult:
    def __init__(self, rows=None):
        self.rows = rows or []

    def scalars(self):
        return self

    def all(self):
        return self.rows


class FakeDocumentQueryResult:
    def __init__(self, document=None):
        self.document = document

    def scalar_one_or_none(self):
        return self.document


class FakeSession:
    def __init__(self, documents=None):
        self.documents = documents or []
        self.deleted = []

    async def execute(self, statement):
        if "SELECT 1" in str(statement):
            return FakeScalarResult(1)
        return FakeQueryResult(self.documents)

    async def delete(self, document):
        self.deleted.append(document)

    async def commit(self):
        return None


class FakeSessionForDelete:
    def __init__(self, document=None):
        self.document = document

    async def execute(self, statement):
        return FakeDocumentQueryResult(self.document)

    async def delete(self, document):
        self.document = None

    async def commit(self):
        return None


class FakeElasticsearch:
    def __init__(self, hits=None):
        self.hits = hits or []
        self.deleted = []

    async def search(self, **kwargs):
        return {"hits": {"hits": self.hits}}

    async def delete(self, **kwargs):
        self.deleted.append(kwargs)

    async def close(self):
        return None


async def make_request(method, url, *, overrides, json=None):
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://testserver") as client:
        app.dependency_overrides.update(overrides)
        try:
            return await client.request(method, url, json=json)
        finally:
            app.dependency_overrides.clear()


def test_root_endpoint():
    response = asyncio.run(make_request("GET", "/", overrides={}))

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_search_documents_returns_db_documents_sorted_by_date():
    older = Document(
        id=1,
        rubrics=["news"],
        text="The quick brown fox jumps over the lazy dog",
        created_date=datetime(2024, 1, 1, 12, 0, 0),
    )
    newer = Document(
        id=2,
        rubrics=["tech"],
        text="A quick fox and a lazy dog are here",
        created_date=datetime(2024, 2, 1, 12, 0, 0),
    )

    fake_session = FakeSession(documents=[newer, older])
    fake_es = FakeElasticsearch(hits=[{"_id": "2"}, {"_id": "1"}])

    async def fake_get_session():
        yield fake_session

    async def fake_get_elasticsearch():
        yield fake_es

    response = asyncio.run(
        make_request(
            "POST",
            "/documents/search",
            json={"query": "quick"},
            overrides={
                get_session: fake_get_session,
                get_elasticsearch: fake_get_elasticsearch,
            },
        )
    )

    assert response.status_code == 200
    payload = response.json()
    assert [item["id"] for item in payload] == [2, 1]
    assert payload[0]["text"] == newer.text
    assert payload[1]["text"] == older.text


def test_delete_document_removes_record():
    document = Document(
        id=10,
        rubrics=["news"],
        text="This document will be deleted",
        created_date=datetime(2024, 3, 1, 12, 0, 0),
    )
    fake_session = FakeSessionForDelete(document=document)
    fake_es = FakeElasticsearch()

    async def fake_get_session():
        yield fake_session

    async def fake_get_elasticsearch():
        yield fake_es

    response = asyncio.run(
        make_request(
            "DELETE",
            "/documents/10",
            overrides={
                get_session: fake_get_session,
                get_elasticsearch: fake_get_elasticsearch,
            },
        )
    )

    assert response.status_code == 200
    assert response.json() == {"message": "Document deleted", "id": 10}
    assert fake_es.deleted == [{"index": "documents", "id": "10", "ignore": [404]}]


def test_delete_document_not_found_returns_404():
    fake_session = FakeSessionForDelete(document=None)
    fake_es = FakeElasticsearch()

    async def fake_get_session():
        yield fake_session

    async def fake_get_elasticsearch():
        yield fake_es

    response = asyncio.run(
        make_request(
            "DELETE",
            "/documents/999",
            overrides={
                get_session: fake_get_session,
                get_elasticsearch: fake_get_elasticsearch,
            },
        )
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Document not found"}


def test_search_documents_returns_all_fields():
    document = Document(
        id=1,
        rubrics=["news", "sport"],
        text="Football news",
        created_date=datetime(2024, 1, 1, 12, 0, 0),
    )

    fake_session = FakeSession(documents=[document])
    fake_es = FakeElasticsearch(hits=[{"_id": "1"}])

    async def fake_get_session():
        yield fake_session

    async def fake_get_elasticsearch():
        yield fake_es

    response = asyncio.run(
        make_request(
            "POST",
            "/documents/search",
            json={"query": "football"},
            overrides={
                get_session: fake_get_session,
                get_elasticsearch: fake_get_elasticsearch,
            },
        )
    )

    assert response.status_code == 200

    assert response.json() == [
        {
            "id": 1,
            "rubrics": ["news", "sport"],
            "text": "Football news",
            "created_date": "2024-01-01T12:00:00",
        }
    ]
