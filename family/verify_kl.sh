#!/bin/bash
# wrapper: from-scratch re-check of all Key Lemma and direct per-m certificates (see verify_kl.py)
cd "$(dirname "$0")" && exec python3 verify_kl.py "$@"
