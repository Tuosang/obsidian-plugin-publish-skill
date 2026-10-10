#!/bin/bash
# Run a file of JavaScript in an Obsidian vault window and print the result.
# usage: obsidian_eval.sh <vault-name> <file.js> [timeout-seconds]
# The obsidian CLI occasionally hangs (window reloading, modal open); this gives up after the timeout
# instead of blocking. Wrap async code as (async()=>{ ...; return JSON.stringify(x) })().
vault="$1"; file="$2"; limit="${3:-20}"
if [ -z "$vault" ] || [ ! -f "$file" ]; then echo "usage: $0 <vault> <file.js> [timeout]" >&2; exit 64; fi
out="$(mktemp -t obsidian_eval)"
(cd "$HOME" && obsidian vault="$vault" eval code="$(cat "$file")" > "$out" 2>&1 &)
for _ in $(seq 1 $((limit * 2))); do [ -s "$out" ] && break; sleep 0.5; done
sleep 0.3
if [ -s "$out" ]; then cat "$out"; rm -f "$out"; else rm -f "$out"; echo "timeout: Obsidian CLI gave no answer in ${limit}s" >&2; exit 2; fi
