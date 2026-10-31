const a = require('assert'); const { withdraw } = require('../src/account');
const acct = { balance: 100 }; a.strictEqual(withdraw(acct, 30), 70); console.log('account ok');
