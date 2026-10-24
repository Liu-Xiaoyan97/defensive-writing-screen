#!/bin/sh
# Install the defensive-writing-screen skill into an agent skills directory.
#
# Usage:
#   sh install.sh                          # -> ~/.agents/skills
#   sh install.sh --dest .agents/skills    # project-level
#   sh install.sh --dest ~/.claude/skills  # Claude Code
#   sh install.sh --force                  # replace an existing install
#   sh install.sh --ref v0.2.0             # pin a tag, branch, or commit
#   sh install.sh --repo you/defensive-writing-screen --ref v0.2.0
#
# Reads the local checkout when run from the repository root; otherwise downloads
# a tarball for the requested ref. No sudo, no package manager, no writes outside
# the destination directory.

set -eu

SKILL_NAME="defensive-writing-screen"
REPO="${DEFENSIVE_WRITING_SCREEN_REPO:-}"
REF="${DEFENSIVE_WRITING_SCREEN_REF:-main}"
DEST="${HOME}/.agents/skills"
FORCE=0

usage() {
  cat <<'EOF'
Install defensive-writing-screen.

Options:
  --dest DIR     skills directory to install into (default: ~/.agents/skills)
  --repo OWNER/REPO  GitHub repository for a remote install (default: $DEFENSIVE_WRITING_SCREEN_REPO)
  --ref REF      git tag, branch, or commit to fetch (default: main)
  --force        replace an existing installation
  -h, --help     show this help
EOF
}

while [ $# -gt 0 ]; do
  case "$1" in
    --dest) DEST="${2:?--dest needs a directory}"; shift 2 ;;
    --ref) REF="${2:?--ref needs a value}"; shift 2 ;;
    --repo) REPO="${2:?--repo needs owner/repo}"; shift 2 ;;
    --force) FORCE=1; shift ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $1" >&2; usage >&2; exit 2 ;;
  esac
done

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
TARGET="${DEST}/${SKILL_NAME}"
TMP_DIR=""
cleanup() { [ -n "$TMP_DIR" ] && rm -rf "$TMP_DIR"; }
trap cleanup EXIT INT TERM

if [ -d "${TARGET}" ] && [ "$FORCE" -ne 1 ]; then
  echo "already installed: ${TARGET}" >&2
  echo "pass --force to replace it" >&2
  exit 1
fi

SOURCE=""
if [ -d "${SCRIPT_DIR}/skills/${SKILL_NAME}" ]; then
  SOURCE="${SCRIPT_DIR}/skills/${SKILL_NAME}"
else
  [ -n "$REPO" ] || { echo "no local checkout found; pass --repo OWNER/REPO for a remote install" >&2; exit 1; }
  command -v curl >/dev/null 2>&1 || { echo "curl is required for remote installs" >&2; exit 1; }
  command -v tar  >/dev/null 2>&1 || { echo "tar is required for remote installs"  >&2; exit 1; }
  TMP_DIR=$(mktemp -d "${TMPDIR:-/tmp}/dws.XXXXXX")
  URL="https://codeload.github.com/${REPO}/tar.gz/${REF}"
  echo "downloading ${URL}" >&2
  curl -fsSL "$URL" | tar -xz -C "$TMP_DIR"
  SOURCE=$(find "$TMP_DIR" -type d -path "*/skills/${SKILL_NAME}" -maxdepth 4 | head -n 1)
  [ -n "$SOURCE" ] || { echo "skill directory not found in downloaded archive" >&2; exit 1; }
fi

[ -f "${SOURCE}/SKILL.md" ] || { echo "invalid source: ${SOURCE}" >&2; exit 1; }

mkdir -p "${DEST}"
STAGING="${DEST}/.${SKILL_NAME}.new.$$"
rm -rf "$STAGING"
cp -R "$SOURCE" "$STAGING"
rm -rf "$TARGET"
mv "$STAGING" "$TARGET"

echo "installed ${SKILL_NAME} -> ${TARGET}" >&2
echo "restart or reload your agent session, then invoke /skill:${SKILL_NAME}" >&2
