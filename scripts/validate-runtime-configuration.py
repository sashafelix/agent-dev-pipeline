#!/usr/bin/env python3
"""Validate and inspect operator model configuration without invoking a model or reading secrets."""
import argparse
import json
from pathlib import Path
import sys

from runtime_configuration import inspect_configuration, load, resolve_configuration
from pipeline_support.common import save_new


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('configuration', type=Path)
    parser.add_argument('--output', type=Path, help='Create a new JSON report; default stdout')
    parser.add_argument('--request', type=Path, help='Optional stage/role request for read-only routing preflight')
    parser.add_argument('--inventory', type=Path, help='Independently trusted host adapter registrations')
    parser.add_argument('--configuration-source', choices=['operator', 'trusted_platform'])
    parser.add_argument('--inventory-source', choices=['operator', 'trusted_platform'])
    args = parser.parse_args()
    try:
        document = load(args.configuration)
        if args.request or args.inventory:
            if not all((args.request, args.inventory, args.configuration_source, args.inventory_source)):
                raise ValueError('Routing preflight requires request, inventory and both independently established sources')
            result = resolve_configuration(document, load(args.request), load(args.inventory), args.configuration_source, args.inventory_source)
        else:
            result = inspect_configuration(document)
        rendered = json.dumps(result, indent=2, sort_keys=True) + '\n'
        if args.output:
            save_new(args.output, rendered)
        else:
            print(rendered, end='')
        return 0
    except (OSError, ValueError, TypeError, RecursionError) as exc:
        print(f'ERROR: {exc}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
