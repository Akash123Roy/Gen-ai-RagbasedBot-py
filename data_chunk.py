from langchain.text_splitter import RecursiveCharacterTextSplitter

class DataChunk():
    def __init__(self):
        pass

    def create_data_chunk(self, data):
        text_splitter = RecursiveCharacterTextSplitter(
            separators= ',',
            chunk_size = 1000,
            chunk_overlap = 150,
            length_function = len
        )
        chunks = text_splitter.split_text(data)
        return chunks