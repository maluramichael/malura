---
title: "Ramda - Validate sequence of numbers"
date: 2018-11-05
tags: javascript ramda code
---

I need to verify that i don't miss any events. So i came up with the concept of a number which needs to increment with every event.

If the numbers aren't consecutive i can tell that the collection is not valid.

## Dataset
```
const data = {
  'transactions': [{
    'transaction': 'A',
    'events': [{
      'number': 0 // <-- Valid
    }, {
      'number': 1 // <-- Valid
    }]
  }, {
    'transaction': 'C',
    'events': [{
      'number': 5 // <-- Valid
    }, {
      'number': 6 // <-- Valid
    }]
  }, {
    'transaction': 'B',
    'events': [{
      'number': 3,
    }, {
      'number': 10,  // <-- Not valid because there are some events are missing
    }]
  }]
};
```
## Code
```
const eventsAreIncrementing = R.pipe(
  R.sortBy(R.prop('number')), // Sort events
  R.map(R.prop('number')), // Get list of event numbers
  R.reduce((acc, current) => {
    if (acc === false) return false; // Skip if we already found a faulty value
    // For the first element return the current one
    // or
    // Check if the current element is an increment of the one before
    if (acc === null || acc + 1 === current) { return current; }
    return false; // Return false to signal that the sequence is not incrementing by one
  }, null),
  R.is(Number) // Reduce returns false if the numbers aren't consecutive otherwise it returns the last number.
  // This is why i check if the result is a number.
);

const allEventsAreIncrementing = R.pipe(
  R.map(R.prop('events')),
  R.all(eventsAreIncrementing)
);

const valid = allEventsAreIncrementing(data.transactions);
```
