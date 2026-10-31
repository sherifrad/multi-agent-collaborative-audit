const a=require('assert');const {pageCount}=require('../src/paginate');
a.strictEqual(pageCount(10,5),2);a.strictEqual(pageCount(11,5),3);console.log('ok');
