const items = [];
exports.add = (t) => { if (typeof t !== 'string' || !t.trim()) throw new Error('empty todo'); items.push({ t: t.trim(), done: false }); return items.length; };
exports.list = () => items.map((i) => ({ ...i }));
exports.reset = () => { items.length = 0; };
