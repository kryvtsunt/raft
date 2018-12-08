PROJECT5: Distributed Replicated Key-Value Store (Raft)
Partners: Tymofii Kryvtsun, Carter Codell

For the Milestone submission we've implemented basic functionality
(leader election, redirection of get/put msgs to leader, respond to get/put msgs by the leader)
to pass first 7 tests.

For the Final submission we've handled all scenarios (crashes and partitions) to pass all 17 tests.
We closely followed the Raft documentation to get an idea of how Distributed Key-Value Store should work.

We have encountered several challenges:
- extremely difficult to debug
- redirection when the leader is unknown
- a lot of edge cases when appending logs
- lack of stability (some tests fail from time to time because of the high latency)
etc.

We debug the program by printing the state of the replicas
at certain point of time or when the new message is arrived.
It is not very helpful though when debugging difficult cases.