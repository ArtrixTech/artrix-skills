#!/usr/bin/env bash
# skills-link —— 重建 ~/.agents/skills 软链 farm
# 技能真身在 ArtrixTech/artrix-skills（公共）与 ArtrixTech/artrix-skills-private（私有）两仓。
# 收录规则：含 SKILL.md 的顶层目录 = 根层技能；不含 SKILL.md 的顶层目录 = 分组目录，
# 其含 SKILL.md 的子目录按组收录（如 matt/、plannotator/）。
# 两端（Mac / ArtrixClaw）路径一致，本脚本在任一仓 clone 里执行均可。
set -euo pipefail
SK="$HOME/GitHub/artrix-skills"
PV="$HOME/GitHub/artrix-skills-private"
DEST="${DEST:-$HOME/.agents/skills}"
META='AGENTS.md Architecture.md docs README.md .gitignore skills-link.sh'

[ -d "$SK" ] || {
  echo "缺 $SK（先 clone ArtrixTech/artrix-skills）" >&2
  exit 1
}
mkdir -p "$DEST"

link_one() { # $1=技能父目录 $2=技能目录名 $3=--replace(可选)
  [ "${3:-}" = "--replace" ] && rm -rf "$DEST/$2"
  ln -sfn "$1/$2" "$DEST/$2"
}

link_repo() {
  for d in "$1"/*/; do
    local n
    n=$(basename "$d")
    [ -d "$d" ] || continue
    case " $META " in *" $n "*) continue ;; esac
    if [ -f "$d/SKILL.md" ]; then
      link_one "$1" "$n" "${2:-}"
    else
      # 分组目录：只收录含 SKILL.md 的子目录
      for sd in "$d"/*/; do
        local sn
        sn=$(basename "$sd")
        [ -f "$sd/SKILL.md" ] || continue
        link_one "$d" "$sn" "${2:-}"
      done
    fi
  done
}

# 清理指向两仓但目标已不存在的失效软链（技能删除/改名后的残留）
prune_farm() {
  for l in "$DEST"/*; do
    [ -L "$l" ] || continue
    local t
    t=$(readlink "$l")
    case "$t" in
      "$SK"/*|"$PV"/*) [ -e "$t" ] || rm -f "$l" ;;
    esac
  done
}

if [ "${1:-}" = "--replace" ]; then
  link_repo "$SK" --replace
  [ -d "$PV" ] && link_repo "$PV" --replace
else
  link_repo "$SK"
  [ -d "$PV" ] && link_repo "$PV"
fi
prune_farm
echo "farm 就绪: $(find "$DEST" -type l | wc -l | tr -d ' ') 个软链 / $(find "$DEST" ! -type l -maxdepth 1 -mindepth 1 | wc -l | tr -d ' ') 个实体残留"