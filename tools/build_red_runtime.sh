#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
WORK="${RED_RUNTIME_WORKDIR:-$ROOT/.work/pokeemerald-expansion}"
UPSTREAM_REPO="https://github.com/rh-hideout/pokeemerald-expansion.git"
UPSTREAM_REF="75b806a3ab57a81ff1eb6179288981f0b3cc3050"

rm -rf "$WORK"
mkdir -p "$(dirname "$WORK")"

git clone --filter=blob:none --no-checkout "$UPSTREAM_REPO" "$WORK"
git -C "$WORK" fetch --depth=1 origin "$UPSTREAM_REF"
git -C "$WORK" checkout --detach FETCH_HEAD

for patch in "$ROOT"/patches/pokeemerald-expansion/*.patch; do
  echo "Checking $(basename "$patch")"
  git -C "$WORK" apply --check "$patch"
  git -C "$WORK" apply "$patch"
done

python3 "$ROOT/tools/audit_upstream_capacity.py" "$WORK"

BUILD_LOG="$WORK/red-build.log"
make -C "$WORK" firered -j"$(nproc)" -O \
  TITLE="PM RED REMAK" \
  GAME_CODE=RDXJ \
  MAKER_CODE=00 2>&1 | tee "$BUILD_LOG"

python3 "$ROOT/tools/verify_red_memory.py" "$BUILD_LOG"

ROM="$WORK/pokefirered.gba"
test -f "$ROM"
python3 "$ROOT/tools/verify_red_gba.py" "$ROM"

# ROM binaries are intentionally ephemeral in RED CI.
rm -f "$ROM"
