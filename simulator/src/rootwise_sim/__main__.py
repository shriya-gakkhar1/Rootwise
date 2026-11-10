"""Command-line entry point for the RootWise simulator."""

import argparse

from .generator import generate_run


def main() -> None:
    parser = argparse.ArgumentParser(prog="rootwise_sim")
    subparsers = parser.add_subparsers(dest="command", required=True)
    generate = subparsers.add_parser("generate", help="generate a deterministic scenario run")
    generate.add_argument("scenario")
    generate.add_argument("--seed", type=int, required=True)
    generate.add_argument("--out", required=True)
    args = parser.parse_args()
    if args.command == "generate":
        generate_run(args.scenario, args.out, args.seed)


if __name__ == "__main__":
    main()
