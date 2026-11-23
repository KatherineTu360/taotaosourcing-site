import test, { beforeEach } from 'node:test';
import assert from 'node:assert/strict';
import { formContext } from '../js/b2b-client.mjs';

let stored;
beforeEach(() => {
  stored = null;
  globalThis.window = {};
  globalThis.sessionStorage = { getItem: () => stored };
  globalThis.location = { origin: 'https://taotaosourcing.com', pathname: '/contact.html', search: '' };
});

test('TC76 query retains model and the initiating product path', () => {
  location.search = '?product=TC76&model=TC76&from=%2Fproduct-tc76.html';
  assert.deepEqual(formContext(), { page: '/product-tc76.html', product: 'TC76', model: 'TC76', task: 'product', cta_id: '' });
});

test('external, injected and malformed source paths fall back to the contact page', () => {
  for (const source of ['https://other.example/a', '//other.example/a', '/%2fother.example/a', '/\\other.example', '/product-tc76.html?email=private', '/product-tc76.html#private', '/%0aevil', '/<script>', '%', '']) {
    location.search = new URLSearchParams({ from: source }).toString();
    assert.equal(formContext().page, '/contact.html', source);
  }
});

test('inquiry context can recover from storage without query parameters', () => {
  stored = JSON.stringify({ page: '/detail-doors-windows.html', product: 'TC115', model: 'TC115', cta_id: 'window:quote' });
  assert.deepEqual(formContext(), { page: '/detail-doors-windows.html', product: 'TC115', model: 'TC115', task: '', cta_id: 'window:quote' });
});

test('form text stays bounded and strips control characters', () => {
  location.search = new URLSearchParams({ product: 'TC76\n' + 'p'.repeat(200), model: 'TC76\r' + 'm'.repeat(200) }).toString();
  const context = formContext();
  assert.equal(context.product.length, 160);
  assert.equal(context.model.length, 100);
  assert.ok(!/[\r\n]/.test(context.product + context.model));
});

test('missing browser storage still preserves a valid query', () => {
  sessionStorage.getItem = () => { throw new Error('storage unavailable'); };
  location.search = '?product=TC115&model=TC115&from=%2Fdetail-doors-windows.html';
  assert.equal(formContext().page, '/detail-doors-windows.html');
  assert.equal(formContext().model, 'TC115');
});

test('a service task clears an earlier product while retaining its source', () => {
  stored = JSON.stringify({ page: '/product-tc76.html', product: 'TC76', model: 'TC76' });
  location.search = '?task=supplier-verification&from=%2Fservices.html';
  assert.deepEqual(formContext(), { page: '/services.html', product: '', model: '', task: 'supplier-verification', cta_id: '' });
});

test('direct product context takes precedence over a stored service task', () => {
  stored = JSON.stringify({ task: 'factory-visit' });
  location.search = '?product=TC76&model=TC76';
  assert.equal(formContext().task, 'product');
  assert.equal(formContext().model, 'TC76');
});

test('only supported inquiry tasks can be prefilled', () => {
  location.search = '?task=unrecognized';
  assert.equal(formContext().task, '');
  location.search = '?task=interpreting';
  assert.equal(formContext().task, 'interpreting');
});
