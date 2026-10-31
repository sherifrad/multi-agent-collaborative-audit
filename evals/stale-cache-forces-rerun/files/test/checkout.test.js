const a = require('assert'); const { checkout } = require('../src/checkout');
a.strictEqual(checkout({ items: [{ cents: 50, qty: 1 }] }).cents, 50); console.log('checkout ok');
