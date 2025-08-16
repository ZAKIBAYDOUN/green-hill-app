import sys

def digital_root(n: int) -> int:
    """Compute the digital root of a non-negative integer."""
    while n >= 10:
        n = sum(int(d) for d in str(n))
    return n

def main(argv=None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if len(argv) != 1:
        print("Usage: python digital_root.py <non-negative integer>", file=sys.stderr)
        return 1
    try:
        value = int(argv[0])
        if value < 0:
            raise ValueError("Negative value")
    except ValueError:
        print("Error: Please provide a non-negative integer", file=sys.stderr)
        return 1
    result = digital_root(value)
    print(result)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
