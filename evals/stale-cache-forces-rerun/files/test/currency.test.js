const a = require('assert'); const { fmt } = require('../src/currency');
a.strictEqual(fmt(1999), '$19.99'); console.log('currency ok');
