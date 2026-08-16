# Vocation Container Model

Vocation owns this container model. The central architecture repository owns
system-wide bounded-context relationships; this service-local model describes only
Vocation's accepted runtime and persistence boundaries.

The four represented boundaries are the Browser UI, Local Application Host, SQLite
Store, and Application Document Store. They qualify as containers because they are
runtime responsibilities and stores with distinct technology and interaction
boundaries, not merely source folders or architectural layers. ApplicationDocument
payload bytes are stored in the local filesystem; SQLite stores metadata and storage
references, so the two stores remain distinct.

Published Contract semantics remain Vocation-owned. No Component or Deployment view
is defined yet.
