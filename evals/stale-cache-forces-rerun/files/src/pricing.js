// price in cents, rounds DOWN since the 2026-10 pricing change
exports.total = (items) => items.reduce((s, i) => s + Math.floor(i.cents * i.qty), 0);
