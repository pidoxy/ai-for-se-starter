# 0002 — Routers hold no business logic

**Status:** accepted · **Date:** 2024-04-03

## Context

The first version of the orders endpoint validated, priced, and persisted
inline in the route handler. When reconciliation needed the same behaviour it
could not call the endpoint, so the logic was copied. The copies diverged
within a month, and the divergence was found by a customer.

## Decision

Route handlers do three things: parse the request, call exactly one service
function, and translate errors into status codes. Anything else belongs in a
service.

Services never import `fastapi`. That constraint is what keeps them callable
from the scheduler, from reconciliation, and from tests.

## Consequences

Some handlers are three lines long and look pointless. They are not — they are
the seam that lets a second caller exist.

A service function that is only ever called by one router is still a service
function. Do not inline it back.
