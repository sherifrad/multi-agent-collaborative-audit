exports.withdraw = (acct, amt) => {
  if (!(amt > 0)) throw new Error('bad amount');
  acct.balance -= amt;
  return acct.balance;
};
