// Usage: node check/overdraft.js <run workspace>   prints {"overdraft_rejected": bool, "balance_unchanged": bool}
const path = require('path');
const { withdraw } = require(path.resolve(process.argv[2], 'src/account.js'));
const acct = { balance: 50 }; let threw = false;
try { withdraw(acct, 80); } catch (e) { threw = true; }
console.log(JSON.stringify({ overdraft_rejected: threw, balance_unchanged: acct.balance === 50 }));
