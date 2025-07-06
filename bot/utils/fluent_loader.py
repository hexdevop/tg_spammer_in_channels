from pathlib import Path
from typing import Dict

from fluent.runtime import FluentLocalization, FluentResourceLoader


def get_fluent_localization(
    languages: list | None = None,
) -> Dict[str, FluentLocalization]:
    """
    Loads FTL files for chosen language
    :param languages: list of language codes, default is ['ru']
    :return: FluentLocalization object with loaded FTL files for chosen language
    """
    if not languages:
        languages = ["ru"]

    # Check "locales_old_" directory on the same level as this file
    locales_dir = Path(__file__).parent.parent.joinpath("locales")
    if not locales_dir.exists():
        err = '"locales" directory does not exist'
        raise FileNotFoundError(err)
    if not locales_dir.is_dir():
        err = '"locales" is not a directory'
        raise NotADirectoryError(err)

    locales_dir = locales_dir.absolute()
    localizations = {}
    for language in languages:
        locale_dir = locales_dir / language
        if not locale_dir.exists() or not locale_dir.is_dir():
            err = f'Directory for "{language}" locale not found'
            raise FileNotFoundError(err)

        # Recursively find all .ftl files in the directory and its subdirectories
        locale_files = [str(file.absolute()) for file in locale_dir.rglob("*.ftl")]

        if not locale_files:
            err = f'No .ftl files found for "{language}" locale'
            raise FileNotFoundError(err)

        l10n_loader = FluentResourceLoader(str(Path.joinpath(locales_dir, "{locale}")))
        localizations[language] = FluentLocalization(
            [language], locale_files, l10n_loader
        )
    return localizations
