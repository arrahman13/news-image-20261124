#!/usr/bin/env python3
"""Entrypoint for the news-image-20261124 make.fun entry.

Copies the committed entry.png into the output directory and verifies it
against the embedded SHA-256 hash. Standard library only; no rendering,
no network.
"""
import hashlib
import os
import shutil
import sys

EXPECTED_SHA256 = "208afdc786c7651666df0b1425daa5831015ec40f6ebf84b7da4541e898d3167"
HERE = os.path.dirname(os.path.abspath(__file__))
ENTRY = os.path.join(HERE, "entry.png")


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or os.path.join(os.getcwd(), "output")
    os.makedirs(out_dir, exist_ok=True)
    dest = os.path.join(out_dir, "entry.png")
    shutil.copyfile(ENTRY, dest)
    digest = hashlib.sha256(open(dest, "rb").read()).hexdigest()
    if digest != EXPECTED_SHA256:
        print(f"SHA-256 mismatch: got {digest}, expected {EXPECTED_SHA256}",
              file=sys.stderr)
        sys.exit(1)
    print(f"entry.png copied to {dest} (sha256 {digest})")


if __name__ == "__main__":
    main()
