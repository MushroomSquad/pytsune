#!/usr/bin/env bash

set -euo pipefail

MIN_UV_VERSION="0.4.0"
RAW_BASE_URL="${BOOTSTRAP_RAW_BASE:-https://raw.githubusercontent.com/OWNER/REPO/main}"
SCAFFOLD_URL="${BOOTSTRAP_SCAFFOLD_URL:-${RAW_BASE_URL}/scaffold.py}"
TMP_SCAFFOLD="$(mktemp /tmp/scaffold.XXXXXX.py)"

cleanup() {
    rm -f "${TMP_SCAFFOLD}"
}

version_ge() {
    local current="$1"
    local minimum="$2"
    [[ "$(printf '%s\n%s\n' "${minimum}" "${current}" | sort -V | tail -n1)" == "${current}" ]]
}

ensure_uv() {
    local current_version

    if command -v uv >/dev/null 2>&1; then
        current_version="$(uv --version | awk '{print $2}')"
        if version_ge "${current_version}" "${MIN_UV_VERSION}"; then
            return
        fi
    fi

    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="${HOME}/.local/bin:${PATH}"

    current_version="$(uv --version | awk '{print $2}')"
    if ! version_ge "${current_version}" "${MIN_UV_VERSION}"; then
        printf 'uv %s or newer is required, found %s\n' "${MIN_UV_VERSION}" "${current_version}" >&2
        exit 1
    fi
}

trap cleanup EXIT

ensure_uv
curl -fsSL "${SCAFFOLD_URL}" -o "${TMP_SCAFFOLD}"
uv run --python 3.11 "${TMP_SCAFFOLD}"
