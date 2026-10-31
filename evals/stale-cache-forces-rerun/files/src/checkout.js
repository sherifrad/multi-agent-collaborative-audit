const { total } = require('./pricing');
exports.checkout = (cart) => ({ cents: total(cart.items), items: cart.items.length });
