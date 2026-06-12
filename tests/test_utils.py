import pytest
from app.utils.serialization import Serialization
from app.utils.pagination import PaginatedResponse
from bson import ObjectId

def test_serialization_fix_ids():
    """Test recursive conversion of ObjectId to string."""
    oid = ObjectId()
    doc = {'_id': oid, 'name': 'Test', 'nested': {'_id': oid, 'items': [{'_id': oid, 'val': 1}]}}
    fixed = Serialization.fix_ids(doc)
    assert isinstance(fixed['_id'], str)
    assert fixed['_id'] == str(oid)
    assert isinstance(fixed['nested']['_id'], str)
    assert isinstance(fixed['nested']['items'][0]['_id'], str)
    assert fixed['name'] == 'Test'

def test_paginated_response_model():
    """Test the PaginatedResponse pydantic model."""
    resp = PaginatedResponse(items=[{'id': 1}], total=10, page=1, size=1, has_more=True)
    assert resp.total == 10
    assert resp.has_more is True