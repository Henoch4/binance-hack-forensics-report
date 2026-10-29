#!/usr/bin/env python3
"""
BINANCE HACK FORENSICS MASTER CONTROLLER
Orchestrates all forensics tools for the Oct 29, 2026 Binance hack investigation.
"""

import asyncio
import argparse
import sys
import os
from datetime import datetime, timezone

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def run_watchlist_poller(args):
    """Run the watchlist poller"""
    from watchlist_poller import main_loop
    await main_loop(args.interval)

async def run_tx_decoder(args):
    """Run transaction decoder"""
    from tx_decoder import main
    await main()

async def run_cross_chain_trace(args):
    """Run cross-chain trace"""
    from cross_chain_trace import main
    await main()

async def run_attribution_check(args):
    """Run Lazarus attribution check"""
    from attribution_check import main
    await main()

async def run_freeze_check(args):
    """Run freeze verification"""
    from freeze_check import main
    await main()

async def run_full_investigation(args):
    """Run complete investigation pipeline"""
    print("=" * 70)
    print("BINANCE HACK - FULL FORENSICS INVESTIGATION")
    print(f"Started: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)
    
    # 1. Attribution check
    print("\n[1/5] ATTRIBUTION OVERLAP CHECK")
    await run_attribution_check(args)
    
    # 2. Freeze verification
    print("\n[2/5] FREEZE STATUS VERIFICATION")
    await run_freeze_check(args)
    
    # 3. Cross-chain trace (needs block numbers)
    print("\n[3/5] CROSS-CHAIN BRIDGE TRACE")
    await run_cross_chain_trace(args)
    
    # 4. Start watchlist poller in background
    print("\n[4/5] STARTING WATCHLIST POLLER (background)")
    print("    Run 'python3 master.py watchlist' in separate terminal for live monitoring")
    
    # 5. Generate summary report
    print("\n[5/5] INVESTIGATION PIPELINE COMPLETE")
    print("    Check generated JSON files for results:")
    print("    - attribution_check.json")
    print("    - freeze_verification.json")
    print("    - bridge_traces.json")
    print("    - binance-hack-forensics-2026-10-29.md (main report)")

def main():
    parser = argparse.ArgumentParser(
        description="Binance Hack Forensics Toolkit - Oct 29, 2026 Investigation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 master.py full              # Run complete investigation pipeline
  python3 master.py watchlist         # Start live address monitoring (10s interval)
  python3 master.py attribution       # Check Lazarus/DPRK overlap
  python3 master.py freeze            # Verify USDT/USDC freeze status
  python3 master.py trace             # Cross-chain bridge tracing
  python3 master.py decode --tx 0x... # Decode specific transaction
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Full investigation
    subparsers.add_parser("full", help="Run complete investigation pipeline")
    
    # Watchlist poller
    watchlist_parser = subparsers.add_parser("watchlist", help="Live address monitoring")
    watchlist_parser.add_argument("--interval", type=int, default=10, help="Poll interval (seconds)")
    
    # Attribution check
    subparsers.add_parser("attribution", help="Lazarus/DPRK overlap check")
    
    # Freeze check
    subparsers.add_parser("freeze", help="USDT/USDC freeze verification")
    
    # Cross-chain trace
    subparsers.add_parser("trace", help="Cross-chain bridge tracing")
    
    # Transaction decoder
    decode_parser = subparsers.add_parser("decode", help="Decode transaction")
    decode_parser.add_argument("--tx", required=True, help="Transaction hash")
    decode_parser.add_argument("--chain", default="ethereum", help="Chain name")
    
    # Report
    subparsers.add_parser("report", help="View main forensics report")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Route to appropriate handler
    handlers = {
        "full": run_full_investigation,
        "watchlist": run_watchlist_poller,
        "attribution": run_attribution_check,
        "freeze": run_freeze_check,
        "trace": run_cross_chain_trace,
        "decode": run_tx_decoder,
    }
    
    if args.command == "report":
        report_path = os.path.join(os.path.dirname(__file__), "binance-hack-forensics-2026-10-29.md")
        if os.path.exists(report_path):
            with open(report_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Handle Windows console encoding
            import sys
            if sys.stdout.encoding and 'cp1252' in sys.stdout.encoding.lower():
                content = content.encode('cp1252', errors='replace').decode('cp1252')
            print(content)
        else:
            print("Report not found. Run 'full' first.")
        return
    
    handler = handlers.get(args.command)
    if handler:
        asyncio.run(handler(args))
    else:
        print(f"Unknown command: {args.command}")
        parser.print_help()

if __name__ == "__main__":
    main()