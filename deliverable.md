In regards of the homework the general guidelines are:
- keep it very simple, clean [architecture and code], don’t forget about testing, documentation, instructions, focus on a full deliverable and strictly on what matters, nothing more nothing less; you will be evaluated on these.
- don’t spend more than 3-4 hours. Deadline is 4 days after receiving the homework, we are considerate of the fact that you have a full-time job and a life. If you can finish earlier even better.

Deliverable:
- write a REST API with two POST endpoints
- first POST endpoint receives a JSON in the form of a document with two fields: a pool-id (numeric) and a pool-values (array of values) and is meant to append (if pool already exists) or insert (new pool) the values to the appropriate pool (as per the id):
  e.g.
        {
           "poolId": 123546,
           "poolValues": [
              1,
              7,
              2,
              6
           ]
        }
- second POST is meant to query a pool, the two fields are pool-id (numeric) identifying the queried pool, and a quantile (in percentile form)
e.g.
        {
           "poolId": 123546,
           "percentile":99.5
        }

- the response from the append is a status field confirming "appended" or "inserted".
- the response from the query has two fields: the calculated quantile and the total count of elements in the pool
- please do not use a library for the quantile calculation if a pool contains less than 100 values.
- focus on high performance if possible (time permitting) and resiliency
- reasoning about high-availability and scalability is a nice-to-have
- no database; no connection to anything needed. Keep it simple.
- your preferred language. The programming language does not need to be a systems language (that performs by definition), so no C/C++/Rust needed (unless this is your preference), really up to you (Python, Go, Java, Scala, ...).


Should you have any questions please feel free to reach out and best of luck!
