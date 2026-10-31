const a = require('assert'); const { total } = require('../src/pricing');
a.strictEqual(total([{ cents: 100, qty: 2 }]), 200); console.log('pricing ok');
