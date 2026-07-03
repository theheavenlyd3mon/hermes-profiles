#!/bin/bash
# verify-guards.sh — Check that all supply chain hardening guards are active
# Returns exit 0 if all pass, exit 1 with warnings if any fail.

FAILED=0

echo "=== Supply Chain Guard Verification ==="
echo ""

# ── 1. Check shell wrapper ───────────────────────────────────────
echo "--- Shell Wrapper ---"
if grep -q 'supply-chain-guard.sh' ~/.zshrc 2>/dev/null; then
  echo "  ✅ ~/.zshrc sources supply-chain-guard.sh"
else
  echo "  ❌ ~/.zshrc missing source line for supply-chain-guard.sh"
  FAILED=1
fi

if [ -f ~/.hermes/scripts/supply-chain-guard.sh ]; then
  echo "  ✅ Script exists at ~/.hermes/scripts/supply-chain-guard.sh"
else
  echo "  ❌ Script missing at ~/.hermes/scripts/supply-chain-guard.sh"
  FAILED=1
fi
echo ""

# ── 2. Check git hook ────────────────────────────────────────────
echo "--- Git Post-Clone Hook ---"
if git config --global init.templateDir 2>/dev/null | grep -q '.git-templates'; then
  echo "  ✅ Git template directory configured"
else
  echo "  ❌ Git template directory not configured"
  FAILED=1
fi

if [ -f ~/.git-templates/hooks/post-checkout ]; then
  echo "  ✅ Hook script exists at ~/.git-templates/hooks/post-checkout"
else
  echo "  ❌ Hook script missing at ~/.git-templates/hooks/post-checkout"
  FAILED=1
fi

if [ -f ~/.hermes/scripts/post-clone-scan.sh ]; then
  echo "  ✅ Scan script exists at ~/.hermes/scripts/post-clone-scan.sh"
else
  echo "  ❌ Scan script missing at ~/.hermes/scripts/post-clone-scan.sh"
  FAILED=1
fi

# Spot-check a few existing repos for the hook
HOOKED=0
UNHOOKED=0
for gitdir in $(find ~ -name ".git" -type d -maxdepth 4 -not -path "*/node_modules/*" -not -path "*/.hermes/*" -not -path "*/Library/*" 2>/dev/null | head -10); do
  if [ -f "$gitdir/hooks/post-checkout" ]; then
    HOOKED=$((HOOKED+1))
  else
    UNHOOKED=$((UNHOOKED+1))
    echo "  ⚠️  Missing hook in: $(dirname "$gitdir")"
  fi
done
echo "  📊 Repos with hook: $HOOKED, without: $UNHOOKED"
echo ""

# ── 3. Check cron advisory job ───────────────────────────────────
echo "--- Cron Advisory Check ---"
# Hermes cron jobs are stored in the hermes config, not user crontab
# Check by looking for the job file
if [ -f ~/.hermes/cron/5d3366224d17.json ] || grep -q "supply-chain-advisory-check" ~/.hermes/config.yaml 2>/dev/null; then
  echo "  ✅ Cron job registered (daily at 9 AM)"
else
  echo "  ⚠️  Cron job not found in local files — may be in Hermes database"
  echo "     Run: hermes cron list"
fi
echo ""

# ── 4. Check egress blocklist ───────────────────────────────────
echo "--- Egress Blocklist (/etc/hosts) ---"
if grep -q "filev2.getsession.org" /etc/hosts 2>/dev/null; then
  echo "  ✅ Session P2P exfiltration endpoints blocked"
else
  echo "  ⚠️  Session P2P endpoints not added to /etc/hosts (needs sudo)"
fi
echo ""

# ── Summary ──────────────────────────────────────────────────────
if [ $FAILED -eq 0 ]; then
  echo "=== ALL GUARDS ACTIVE ==="
else
  echo "=== $FAILED guard(s) failed — see above ==="
fi
exit $FAILED
