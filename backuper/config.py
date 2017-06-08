import ConfigParser


def get_list_from_config_value(value):
    """

    :type value: str
    :return: list[str]
    """
    return map(lambda item: item.strip(), value.split(','))


def convert_config_items_to_dict(items, iterable_fields=None):
    """

    :type items: list[(str,str)]
    :type iterable_fields list[str]
    :return: dict
    """
    result = {}
    for key, value in items:
        result[key] = get_list_from_config_value(value) if iterable_fields and key in iterable_fields else value
    return result


class FtpConfigKeeper:
    def __init__(self, main_config_parser):
        """

        :type main_config_parser: ConfigParser.ConfigParser
        """
        self._main_config_parser = main_config_parser

    def get_full_config(self, current_config):
        """

        :type current_config: dict
        :return: dict[str,str]
        """
        result = dict(self._main_config_parser.items(current_config['extends'])) if 'extends' in current_config else {}
        result.update(current_config)
        return result
