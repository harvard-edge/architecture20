#!/usr/bin/env bash
set -euo pipefail

version="5.3.0"
sha256="6c07e68584b2e2ce2f89fe06e1246dfead3eb36b46b340e7d93524f29dcff6c5"
archive="${RUNNER_TEMP:-/tmp}/epubcheck-${version}.zip"
install_root="${RUNNER_TEMP:-/tmp}/arch2-epubcheck"
package_root="${install_root}/epubcheck-${version}"
bin_dir="${install_root}/bin"

if [[ ! -f "${package_root}/epubcheck.jar" ]]; then
  curl --fail --location --retry 3 \
    --output "${archive}" \
    "https://github.com/w3c/epubcheck/releases/download/v${version}/epubcheck-${version}.zip"
  if sha256sum --help 2>&1 | grep -q -- "--check"; then
    echo "${sha256}  ${archive}" | sha256sum --check --strict
  else
    actual_sha256="$(shasum -a 256 "${archive}" | awk '{print $1}')"
    if [[ "${actual_sha256}" != "${sha256}" ]]; then
      echo "EPUBCheck archive checksum mismatch" >&2
      exit 1
    fi
  fi
  rm -rf "${install_root}"
  mkdir -p "${install_root}"
  unzip -q "${archive}" -d "${install_root}"
fi

mkdir -p "${bin_dir}"
java_bin=""
if [[ -n "${JAVA_HOME:-}" && -x "${JAVA_HOME}/bin/java" ]]; then
  java_bin="${JAVA_HOME}/bin/java"
elif [[ -x "/opt/homebrew/opt/openjdk/bin/java" ]]; then
  java_bin="/opt/homebrew/opt/openjdk/bin/java"
elif [[ -x "/usr/local/opt/openjdk/bin/java" ]]; then
  java_bin="/usr/local/opt/openjdk/bin/java"
else
  java_bin="$(command -v java || true)"
fi
if [[ -z "${java_bin}" ]]; then
  echo "A Java runtime is required for EPUBCheck" >&2
  exit 1
fi
printf '#!/usr/bin/env bash\nexec "%s" -jar "%s" "$@"\n' \
  "${java_bin}" "${package_root}/epubcheck.jar" > "${bin_dir}/epubcheck"
chmod +x "${bin_dir}/epubcheck"

if [[ -n "${GITHUB_PATH:-}" ]]; then
  echo "${bin_dir}" >> "${GITHUB_PATH}"
else
  echo "Add ${bin_dir} to PATH" >&2
fi
