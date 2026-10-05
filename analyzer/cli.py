import sys
from pathlib import Path

from analyzer.analyze import CodeAnalyzer


def print_impact(
    analyzer,
    symbol
):

    affected = analyzer.find_impact(
        symbol
    )

    print(
        f"\nImpact of: {symbol}"
    )

    if not affected:

        print(
            "\n  No potentially affected "
            "symbols found."
        )

        return {}

    print(
        "\nPotentially affected:"
    )

    for item, information in affected.items():

        print(
            f"\n  {item}"
        )

        file_path = information.get(
            "file"
        )

        if file_path:

            print(
                f"    File: {file_path}"
            )

        line_number = information.get(
            "line"
        )

        if line_number:

            print(
                f"    Line: {line_number}"
            )

        print(
            f"    Relationship: "
            f"{information.get('relation', 'unknown')}"
        )

        print(
            f"    Impact: "
            f"{information.get('impact', 'UNKNOWN')}"
        )

        print(
            f"    Risk: "
            f"{information.get('risk', 'UNKNOWN')}"
        )

        confidence = information.get(
            "confidence"
        )

        if confidence is not None:

            print(
                f"    Confidence: "
                f"{confidence}%"
            )

        reason = information.get(
            "reason"
        )

        if reason:

            print(
                f"    Reason: "
                f"{reason}"
            )

        print(
            "    Path:"
        )

        for step in information.get(
            "path",
            []
        ):

            print(
                f"      ↓ {step}"
            )

    return affected


def print_overall_risk(
    analyzer,
    changed_symbols,
    all_affected
):

    summary = (
        analyzer.calculate_overall_risk(
            all_affected
        )
    )

    print(
        "\nOverall Risk"
    )

    print(
        "===================="
    )

    print(
        f"Risk Level: "
        f"{summary['risk']}"
    )

    print(
        f"Changed Symbols: "
        f"{len(changed_symbols)}"
    )

    print(
        f"Affected Symbols: "
        f"{summary['affected_symbols']}"
    )

    print(
        f"Affected Files: "
        f"{summary['affected_files']}"
    )

    print(
        f"HIGH Risk: "
        f"{summary['high']}"
    )

    print(
        f"MEDIUM Risk: "
        f"{summary['medium']}"
    )

    print(
        f"LOW Risk: "
        f"{summary['low']}"
    )


def main():

    if len(sys.argv) < 2:

        print(
            "Usage: python -m analyzer.cli "
            "<repository> "
            "[--symbol <symbol>] "
            "[--from <commit> --to <commit>]"
        )

        return

    repository = Path(
        sys.argv[1]
    )

    if not repository.exists():

        print(
            f"Repository not found: "
            f"{repository}"
        )

        return

    if not repository.is_dir():

        print(
            f"Repository is not a directory: "
            f"{repository}"
        )

        return

    requested_symbol = None
    old_commit = None
    new_commit = None

    index = 2

    while index < len(sys.argv):

        argument = sys.argv[index]

        if argument == "--symbol":

            if index + 1 >= len(sys.argv):

                print(
                    "Missing symbol after --symbol"
                )

                return

            requested_symbol = (
                sys.argv[index + 1]
            )

            index += 2

        elif argument == "--from":

            if index + 1 >= len(sys.argv):

                print(
                    "Missing commit after --from"
                )

                return

            old_commit = (
                sys.argv[index + 1]
            )

            index += 2

        elif argument == "--to":

            if index + 1 >= len(sys.argv):

                print(
                    "Missing commit after --to"
                )

                return

            new_commit = (
                sys.argv[index + 1]
            )

            index += 2

        else:

            print(
                f"Unknown option: {argument}"
            )

            return

    if (
        old_commit is not None
        and new_commit is None
    ):

        print(
            "Missing --to commit"
        )

        return

    if (
        old_commit is None
        and new_commit is not None
    ):

        print(
            "Missing --from commit"
        )

        return

    analyzer = CodeAnalyzer(
        str(repository)
    )

    print(
        "Code Impact Analyzer"
    )

    print(
        "===================="
    )

    print(
        f"\nRepository: {repository}"
    )

    if requested_symbol:

        print(
            "\nChanged Symbol:"
        )

        print(
            f"  {requested_symbol}"
        )

        affected = print_impact(
            analyzer,
            requested_symbol
        )

        print_overall_risk(
            analyzer,
            [requested_symbol],
            affected
        )

        return

    if (
        old_commit is not None
        and new_commit is not None
    ):

        print(
            "\nComparing commits:"
        )

        print(
            f"  From: {old_commit}"
        )

        print(
            f"  To:   {new_commit}"
        )

        changed_symbols = (
            analyzer.find_changed_symbols_between(
                old_commit,
                new_commit
            )
        )

    else:

        changed_symbols = (
            analyzer.find_changed_symbols()
        )

    print(
        "\nChanged Symbols:"
    )

    if not changed_symbols:

        print(
            "  No changed symbols found."
        )

        print_overall_risk(
            analyzer,
            [],
            {}
        )

        return

    for symbol in changed_symbols:

        print(
            f"  {symbol}"
        )

    print(
        "\nPotentially affected:"
    )

    all_affected = {}

    for symbol in changed_symbols:

        affected = print_impact(
            analyzer,
            symbol
        )

        for item, information in (
            affected.items()
        ):

            if item not in all_affected:

                all_affected[item] = information

    print_overall_risk(
        analyzer,
        changed_symbols,
        all_affected
    )


if __name__ == "__main__":
    main()