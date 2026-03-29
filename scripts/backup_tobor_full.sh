#!/usr/bin/env bash
set -euo pipefail

SOURCE_DIR="/data/.openclaw"
REPO_SLUG="mpatti/tobor"
GIT_USER_NAME="Mike Patti"
GIT_USER_EMAIL="mpatti@mac.com"
TZ_NAME="America/New_York"
PART_SIZE="45m"

TMPROOT="$(mktemp -d /tmp/tobor-daily-backup-XXXXXX)"
trap 'rm -rf "$TMPROOT"' EXIT

TS="$(TZ="$TZ_NAME" date +%Y%m%d-%H%M%S)"
HUMAN_TS="$(TZ="$TZ_NAME" date '+%Y-%m-%d %H:%M:%S %Z')"
ARCHIVE_BASENAME="tobor-openclaw-full-${TS}.tar.gz"
ARCHIVE_PATH="$TMPROOT/$ARCHIVE_BASENAME"
PARTS_DIR="$TMPROOT/parts"
REPO_DIR="$TMPROOT/repo"
BACKUP_DIR="$REPO_DIR/backups/latest"

mkdir -p "$PARTS_DIR" "$REPO_DIR"

# Create fresh archive of the full OpenClaw state tree.
tar -C /data -czf "$ARCHIVE_PATH" .openclaw
SHA256="$(sha256sum "$ARCHIVE_PATH" | awk '{print $1}')"
split -b "$PART_SIZE" -d -a 3 "$ARCHIVE_PATH" "$PARTS_DIR/${ARCHIVE_BASENAME}.part-"

# Prepare a fresh single-snapshot repo so daily backups replace prior contents.
git -C "$REPO_DIR" init -b main >/dev/null
git -C "$REPO_DIR" config user.name "$GIT_USER_NAME"
git -C "$REPO_DIR" config user.email "$GIT_USER_EMAIL"
git -C "$REPO_DIR" remote add origin "https://x-access-token:$(gh auth token)@github.com/${REPO_SLUG}.git"

mkdir -p "$BACKUP_DIR"
cp "$PARTS_DIR"/* "$BACKUP_DIR/"
printf '%s  %s\n' "$SHA256" "$ARCHIVE_BASENAME" > "$BACKUP_DIR/SHA256SUMS.txt"

cat > "$REPO_DIR/README.md" <<EOF
# Tobor Backup Repo

Private rolling backup storage for recreating this OpenClaw instance.

## Included in this backup

This repo stores a split archive of the full `/data/.openclaw` state tree from the source machine at the time of backup.

That includes:
- workspace files
- memory files
- sessions
- config
- credentials
- Telegram state
- browser state
- agent state

## Sensitivity

This backup contains secrets and private state.
Keep this repository private.

## Latest backup set

- Timestamp: $HUMAN_TS
- Archive basename: $ARCHIVE_BASENAME
- SHA-256: $SHA256

## Restore

1. Download all part files from `backups/latest/`.
2. Reassemble the archive:

```bash
cat $ARCHIVE_BASENAME.part-* > $ARCHIVE_BASENAME
sha256sum $ARCHIVE_BASENAME
```

Expected checksum:

```text
$SHA256
```

3. Stop OpenClaw on the target machine.
4. Restore into `/data`:

```bash
sudo tar -C /data -xzf $ARCHIVE_BASENAME
```

5. Start OpenClaw again.

## Notes

- This is a state backup, not a package-manager backup of the OpenClaw npm installation itself.
- In practice, restoring `/data/.openclaw` is the critical piece for recreating the same assistant state and memory.
- This repo is intentionally maintained as a rolling latest snapshot to avoid runaway history growth from giant binary backups.
EOF

cat > "$REPO_DIR/backup-metadata.json" <<EOF
{
  "createdAt": "$(TZ="$TZ_NAME" date --iso-8601=seconds)",
  "sourcePath": "$SOURCE_DIR",
  "archiveBasename": "$ARCHIVE_BASENAME",
  "sha256": "$SHA256",
  "containsSecrets": true,
  "notes": [
    "Split archive parts are stored under backups/latest/.",
    "This backup contains the full /data/.openclaw state tree.",
    "The repository is maintained as a rolling latest snapshot."
  ]
}
EOF

git -C "$REPO_DIR" add README.md backup-metadata.json backups/latest
git -C "$REPO_DIR" commit -m "Update rolling OpenClaw state backup (${TS})" >/dev/null
git -C "$REPO_DIR" push --force origin main >/dev/null

echo "Backup complete: $ARCHIVE_BASENAME"
echo "SHA256: $SHA256"
