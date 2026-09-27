"""Main entry point for the Photon laser-tag application."""

from player_entry import run_player_entry


def main() -> None:
    # Sprint 2 UI entry point.
    # Database/UDP integration can be passed to run_player_entry as a callback.
    run_player_entry()


if __name__ == "__main__":
    main()
