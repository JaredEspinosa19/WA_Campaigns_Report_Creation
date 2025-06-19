
from models.llm_model import LLMModel



def get_shots_list(path: str)-> list:
    """
    Reads a file and returns a list of lines.
    :param path: Path to the file.
    :return: List of lines in the file.
    """
    shots_list = []
    with open(path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        lines = lines.split(' ')
        shots_list = [lines[0], lines[1]] # Shot_name, Date(YYYY-MM-DD HH:MM:SS)

    return shots_list

def

def get_conversations(shots_list: list) -> str:


def main()
    
    llm = LLMModel(model_name='gemma3:12b')

