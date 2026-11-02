@echo off
cd c:\Users\hanee\Enterprise RAG Platform
python -c "import sys; sys.path.insert(0, '.'); from fastapi.testclient import TestClient; from app.main import app; client = TestClient(app); 

# Test ingest
response = client.post('/ingest/', json={'doc_id': 'doc1', 'text': 'This is a test document about machine learning.', 'metadata': {'source': 'test'}, 'tenant_id': 'tenant1'})
print(f'Ingest status: {response.status_code}')
print(f'Ingest response: {response.json()}')
assert response.status_code == 200
data = response.json()
assert data['doc_id'] == 'doc1'
assert data['chunks'] > 0
assert 'trace_id' in data
print('Ingest test PASSED')

# Test query
client.post('/ingest/', json={'doc_id': 'doc1', 'text': 'This is a test document about machine learning.', 'metadata': {'source': 'test'}, 'tenant_id': 'tenant1'})
response = client.post('/query/', json={'query': 'machine learning', 'top_k': 3, 'tenant_id': 'tenant1'})
print(f'Query status: {response.status_code}')
data = response.json()
assert 'answer' in data
assert 'citations' in data
assert len(data['citations']) > 0
assert 'trace_id' in data
print('Query test PASSED')

# Test health
response = client.get('/health/')
print(f'Health status: {response.status_code}')
data = response.json()
assert data['status'] == 'ok'
assert 'db' in data
assert 'redis' in data
assert 'latency_ms' in data
print('Health test PASSED')

# Test auth
response = client.post('/auth/login/', json={'user_id': 'user1', 'tenant_id': 'tenant1'})
print(f'Auth status: {response.status_code}')
data = response.json()
assert data['user_id'] == 'user1'
assert data['tenant_id'] == 'tenant1'
print('Auth test PASSED')

print\\nAll tests completed successfully!