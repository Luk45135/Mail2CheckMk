from pathlib import Path

def main() -> None:

    Path("plaintext-emails").mkdir(parents=True, exist_ok=True)



if __name__ == "__main__":
    main()
