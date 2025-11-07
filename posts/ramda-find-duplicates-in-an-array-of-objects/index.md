---
title: "Ramda - Find duplicates in an array of objects"
date: 2018-11-05
tags: code ramda javascript
---

For my current project i need to verify that a list of transactions doesn't contain any duplicates based on the transaction id.

So i'll show you how i search for duplicates in lists based on a property.
```
const R = require('ramda');
const data = {
  'transactions': [{ // Transactions have to be unique
    'transaction': 'A',
    'events': [{
      'number': 0
    }, {
      'number': 1
    }]
  }, {
    'transaction': 'B',
    'events': [{
      'number': 0,
    }, {
      'number': 1,
    }]
  }]
};

// Group each transactions by its transaction id
const groupByTransaction = R.groupBy(R.prop('transaction'));

// Get the length of each transaction group
const mapLengthOfEachGroup = R.mapObjIndexed(R.prop('length'));

// Creates an array containing only the number of elements in each group. Best case would be [1, 1, 1...]
const arrayOfGroupLengths = R.values;

// Check if an element is greater than 1
const ensureArrayContainsOnlyOnes = R.any(R.lte(2));

const hasDuplicates = R.pipe(
  groupByTransaction,
  mapLengthOfEachGroup,
  arrayOfGroupLengths,
  ensureArrayContainsOnlyOnes
);

hasDuplicates(data.transactions);
```
