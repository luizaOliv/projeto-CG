import os


def resolve(filename):
    """
    Resolve o caminho do arquivo independentemente do caminho da execução do comando
    """
    return '{0}\\assets\{1}'.format(os.path.dirname(os.path.abspath(__file__)), filename)
