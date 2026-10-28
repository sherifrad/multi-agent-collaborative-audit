# Systems, Embedded and High-Performance Pack

- **Memory:** no leaks, double-free or use-after-free; deterministic cleanup (RAII or equivalent).
- **Hot paths:** no heap allocation in audio/render loops; bound every queue.
- **Concurrency:** lock-ordering to avoid deadlock; graceful shutdown on SIGTERM/SIGINT via atomic flags.
- **Tests to include:** sanitizer builds (ASan/TSan/UBSan), stress and soak runs, fault injection on allocation/IO.
