import sys
from pathlib import Path

from analyzer.analyze import CodeAnalyzer


def main():

    if len(sys.argv) < 2:

        print(
            "Usage: python -m analyzer.cli "
            "<repository> [--symbol <symbol>]"
        )

        return

    repository = Path(
        sys.argv[1]
    )

    if not repository.exists():

        print(
            f"Repository not found: {repository}"
        )

        return

    if not repository.is_dir():

        print(
            f"Repository is not a directory: "
            f"{repository}"
        )

        return

    requested_symbol = None

    if len(sys.argv) > 2:

        if sys.argv[2] != "--symbol":

            print(
                "Unknown option: "
                f"{sys.argv[2]}"
            )

            return

        if len(sys.argv) < 4:

            print(
                "Missing symbol after --symbol"
            )

            return

        requested_symbol = sys.argv[3]

    analyzer = CodeAnalyzer(
        str(repository)
    )

    print("Code Impact Analyzer")
    print("====================")

    print(
        f"\nRepository: {repository}"
    )

    if requested_symbol:

        print(
            f"\nChanged Symbol:"
        )

        print(
            f"  {requested_symbol}"
        )

        affected = analyzer.find_impact(
            requested_symbol
        )

        print(
            "\nPotentially affected:"
        )

        if not affected:

            print(
                "  No potentially affected "
                "symbols found."
            )

            return

        for item, information in affected.items():

            print(
                f"\n  {item}"
            )

            if information.get("file"):

                print(
                    f"    File: "
                    f"{information['file']}"
                )

            if information.get("line"):

                print(
                    f"    Line: "
                    f"{information['line']}"
                )

            print(
                f"    Relationship: "
                f"{information.get('relation', 'unknown')}"
            )

            print(
                f"    Impact: "
                f"{information.get('impact', 'UNKNOWN')}"
            )

            print("    Path:")

            for step in information.get(
                "path",
                []
            ):

                print(
                    f"      ↓ {step}"
                )

        return

    changed_symbols = (
        analyzer.find_changed_symbols()
    )

    print("\nChanged Symbols:")

    if not changed_symbols:

        print(
            "  No changed symbols found."
        )

        return

    for symbol in changed_symbols:

        print(
            f"  {symbol}"
        )

    print("\nPotentially affected:")

    found_impact = False

    for symbol in changed_symbols:

        affected = analyzer.find_impact(
            symbol
        )

        if not affected:
            continue

        found_impact = True

        print(
            f"\nImpact of: {symbol}"
        )

        for item, information in affected.items():

            print(
                f"\n  {item}"
            )

            if information.get("file"):

                print(
                    f"    File: "
                    f"{information['file']}"
                )

            if information.get("line"):

                print(
                    f"    Line: "
                    f"{information['line']}"
                )

            print(
                f"    Relationship: "
                f"{information.get('relation', 'unknown')}"
            )

            print(
                f"    Impact: "
                f"{information.get('impact', 'UNKNOWN')}"
            )

            print("    Path:")

            for step in information.get(
                "path",
                []
            ):

                print(
                    f"      ↓ {step}"
                )

    if not found_impact:

        print(
            "  No potentially affected "
            "symbols found."
        )


if __name__ == "__main__":
    main()