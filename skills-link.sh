#!/usr/bin/env bash
# skills-link —— 重建 ~/.agents/skills 软链 farm
# 技能真身在 ArtrixTech/artrix-skills（公共）与 ArtrixTech/artrix-skills-private（私有）两仓；
# 两端（Mac / ArtrixClaw）路径一致，本脚本在任一仓 clone 里执行均可。
set -euo pipefail
SK="$HOME/GitHub/artrix-skills"
PV="$HOME/GitHub/artrix-skills-private"
DEST="${DEST:-$HOME/.agents/skills}"
META='AGENTS.md Architecture.md docs README.md .gitignore skills-link.sh'

[ -d "$SK" ] || { echo "缺 $SK（先 clone ArtrixTech/artrix-skills）" >&2; exit 1; }
mkdir -p "$DEST"

link_repo() {
  for d in "$1"/*/; do
    n=$(basename "$d"); [ -d "$d" ] || continue
    case " $META " in *" $n "*) continue;; esac
    [ "$2" = "--replace" ] && rm -rf "$DEST/$n"
    ln -sfn "$1/$n" "$DEST/$n"
  done
}

if [ "${1:-}" = "--replace" ]; then
  link_repo "$SK" --replace
  [ -d "$PV" ] && link_repo "$PV" --replace
else
  link_repo "$SK"; [ -d "$PV" ] && link_repo "$PV"
fi
echo "farm 就绪: $(find "$DEST" -type l | wc -l | tr -d ' ') 个软链 / $(find "$DEST" ! -type l -maxdepth 1 -mindepth 1 | wc -l | tr -d ' ') 个实体残留"