import textwrap

class PromptTemplate():
    def __init__(self):
        pass

    def make_prompt(self, query, relevant_passage):
        escaped = relevant_passage.replace("'", "").replace('"', "").replace("\n", " ")
        prompt = textwrap.dedent("""You are a helpful and informative bot that answers questions using text from the reference passage included below. \
        Be sure to respond in a complete sentence, being comprehensive, including all relevant background information. \
        Be descriptive when user ask you to provide descriptive answers. In descriptive answers try to answer using bullet points and be very specific to the content\
        However, you are talking to a non-technical audience, so be sure to break down complicated concepts and \
        strike a friendly and converstional tone. \
        If the passage is irrelevant to the answer, you may ignore it.
        QUESTION: '{query}'
        PASSAGE: '{relevant_passage}'

            ANSWER:
        """).format(query=query, relevant_passage=escaped)

        return prompt
