"""Einstiegspunkt: führt die Pipeline-Schritte der Reihe nach aus."""

from de_projekt import ingestion, serving, storage, transformation


def main() -> None:
    ingestion.run()
    storage.run()
    transformation.run()
    serving.run()


if __name__ == "__main__":
    main()
