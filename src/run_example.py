from pathlib import Path
import sys

from thumbnail_service import GameImage, InfraiImageClient, make_thumbnail


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).with_name("sample.bin")
    if not path.exists():
        path.write_bytes(b"demo image bytes")
    image = GameImage("player-42", "player", path.name, path.read_bytes())
    result = make_thumbnail(InfraiImageClient(), image)
    print(result["data"])


if __name__ == "__main__":
    main()
