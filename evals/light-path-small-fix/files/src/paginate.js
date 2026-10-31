exports.pageCount = (n, size) => Math.floor(n / size) + (n % size > 0 ? 0 : 0);
