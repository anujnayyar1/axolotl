"""Module containing prompters"""

import dataclasses
import logging
from enum import auto, Enum
from typing import List, Union, Generator

IGNORE_TOKEN_ID = -100


class PromptStyle(Enum):
    """
    Enum for prompt styles
    """

    INSTRUCT = "instruct"
    CHAT = "chat"


class AlpacaPrompter:
    """
    Base class for alpaca prompters
    """

    system_prompt = "Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.\n\n"
    system_no_input_prompt = "Below is an instruction that describes a task. Write a response that appropriately completes the request.\n\n"
    prompt_style = None

    def __init__(self, prompt_style=PromptStyle.INSTRUCT.value):
        self.prompt_style = prompt_style if prompt_style else PromptStyle.INSTRUCT.value
        self.match_prompt_style()

    def match_prompt_style(self):
        if self.prompt_style == PromptStyle.INSTRUCT.value:
            self.prompt_input = (
                self.system_prompt
                + "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n"
            )
            self.prompt_no_input = (
                self.system_no_input_prompt
                + "### Instruction:\n{instruction}\n\n### Response:\n"
            )
            self.response_split = "### Response:"
        if self.prompt_style == PromptStyle.CHAT.value:
            self.prompt_input = (
                self.system_prompt + "USER: {instruction}\n{input}\nASSISTANT:"
            )
            self.prompt_no_input = (
                self.system_no_input_prompt + "USER: {instruction}\nASSISTANT:"
            )
            self.response_split = "ASSISTANT:"

    def build_prompt(
        self,
        instruction: str,
        input: Union[None, str] = None,  # pylint: disable=redefined-builtin
        output: Union[None, str] = None,
    ) -> Generator[str, None, None]:
        # returns the full prompt from instruction and optional input
        # if a label (=response, =output) is provided, it's also appended.
        if input:
            res = self.prompt_input.format(instruction=instruction, input=input)
        else:
            res = self.prompt_no_input.format(instruction=instruction)
        if output:
            res = f"{res}{output}"
        yield res

    def get_response(self, output: str) -> str:
        return output.split(self.response_split)[1].strip()


class UnpromptedPrompter(AlpacaPrompter):
    """
    Prompter for alpaca no system prompt
    """

    system_prompt = ""
    system_no_input_prompt = ""


class JeopardyPrompter(AlpacaPrompter):
    """
    Prompter for Jeopardy
    """

    prompt_input = "Below is a Jeopardy clue paired with input providing the category of the clue. Write a concise response that best answers tbe clue given the category.\n\n### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n"


class MultipleChoiceExplainPrompter(AlpacaPrompter):
    """
    Prompter for multiple choice explain
    """

    system_prompt = (
        "Choose the answer that best answers the question. Explain your reasoning."
    )


class MultipleChoiceConcisePrompter(AlpacaPrompter):
    """
    Prompter for multiple choice concise
    """

    prompt_input = "Choose the answer that best answers the question. Be concise in your response.\n\nUSER: {instruction}\n{input}\nASSISTANT:\n"


class SummarizeTLDRPrompter(AlpacaPrompter):
    """
    Prompter for summarize TLDR
    """

    prompt_no_input = (
        "USER: Summarize the following article as a TL;DR.\n{instruction}\nASSISTANT:"
    )


class CompletionPrompter:
    """
    Prompter for completion
    """

    def build_prompt(
        self,
        instruction: str,
        input=None,  # pylint: disable=redefined-builtin, unused-argument
        output=None,  # pylint: disable=unused-argument
    ) -> Generator[str, None, None]:
        yield instruction

    def get_response(self, output: str) -> str:
        return output.strip()


class GPTeacherPrompter(AlpacaPrompter):
    """
    Prompter for GPTeacher
    """


class NomicGPT4AllPrompter(AlpacaPrompter):
    """
    Prompter for NomicGPT4All
    """


class ReflectAlpacaPrompter:
    """
    Prompter for ReflectAlpaca
    """

    system_prompt = "Below is an instruction that describes a task, paired with an input that provides further context. You, the Assistant, should generate a response as if it were an abstract for an academic or technical paper on the query along with a methodology. Then generate an Agent Reflection where you create a long form response as if from subject matter expert, be verbose, diligent, and creative in your application of knowledge, apply it through the lens of the response generated by the assistant. Look for flawed reasoning, faulty logic, or other mistakes in the method. Finally, generate a final response and method for the user with the Assistant abstract and Reflection analysis as augmentations to the generation\n\n"
    system_no_input_prompt = "Below is an instruction that describes a task. You, the Assistant, should generate a response as if it were an abstract for an academic or technical paper on the query along with a methodology. Then generate an Agent Reflection where you create a long form response as if from subject matter expert, be verbose, diligent, and creative in your application of knowledge, apply it through the lens of the response generated by the assistant. Look for flawed reasoning, faulty logic, or other mistakes in the method. Finally, generate a final response and method for the user with the Assistant abstract and Reflection analysis as augmentations to the generation\n\n"

    prompt_input = (
        "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n"
    )
    prompt_no_input = "### Instruction:\n{instruction}\n\n### Response:\n"
    agent_label = "### Thought:\n{output}\n\n### Agent Reflection:\n{reflection}\n\n### Final Response:\n{corrected}"
    response_split = "### Response:"

    def __init__(self, prompt_style="instruct"):
        self.prompt_style = prompt_style
        self.match_prompt_style()

    def match_prompt_style(self):
        if self.prompt_style == PromptStyle.INSTRUCT.value:
            self.prompt_input = (
                self.system_prompt
                + "### Instruction:\n{instruction}\n\n### Input:\n{input}\n\n### Response:\n"
            )
            self.prompt_no_input = (
                self.system_no_input_prompt
                + "### Instruction:\n{instruction}\n\n### Response:\n"
            )
            self.agent_label = "### Thought:\n{output}\n\n### Agent Reflection:\n{reflection}\n\n### Final Response:\n{corrected}"
            self.response_split = "### Final Response:"
        if self.prompt_style == PromptStyle.CHAT.value:
            self.prompt_input = (
                self.system_prompt + "USER: {instruction}\n{input}\nASSISTANT:"
            )
            self.prompt_no_input = (
                self.system_no_input_prompt + "USER: {instruction}\nASSISTANT:"
            )
            self.agent_label = (
                "\nTHOUGHT: {output}\nASSISTANT REFLECTION: {reflection}\nASSISTANT:"
            )
            self.response_split = "ASSISTANT:"

    def build_prompt(
        self,
        instruction: str,
        input: Union[None, str] = None,  # pylint: disable=redefined-builtin
        output: Union[None, str] = None,
        reflection: Union[None, str] = None,
        corrected: Union[None, str] = None,
    ) -> Generator[str, None, None]:
        # returns the full prompt from instruction and optional input
        # if a label (=response, =output) is provided, it's also appended.
        if input:
            res = self.prompt_input.format(instruction=instruction, input=input)
        else:
            res = self.prompt_no_input.format(instruction=instruction)
        if output and reflection and corrected:
            label = self.agent_label.format(
                output=output, reflection=reflection, corrected=corrected
            )
            res = f"{res}{label}"
        yield res

    def get_response(self, output: str) -> str:
        return output.split(self.response_split)[1].strip()


class SeparatorStyle(Enum):
    """Different separator style."""

    SINGLE = auto()
    TWO = auto()
    DOLLY = auto()


# TODO clean this 💩 up
@dataclasses.dataclass
class Conversation:
    """A class that keeps all conversation history."""

    system: str
    roles: List[str]
    messages: List[List[str]]
    offset: int
    sep_style: SeparatorStyle = SeparatorStyle.SINGLE
    sep: str = "###"
    sep2: str = None

    def get_prompt(self) -> Generator[str, None, None]:
        seps = [self.sep, self.sep2]
        preamble = self.system + seps[0]
        yield preamble
        for _, (role, message) in enumerate(self.messages):
            if message:
                yield (role + ":", " " + message)
            else:
                logging.warning(f"role with empty message: {role}")
                yield (role + ":",)

    def copy(self):
        return Conversation(
            system=self.system,
            roles=self.roles,
            messages=[[x, y] for x, y in self.messages],
            offset=self.offset,
            sep_style=self.sep_style,
            sep=self.sep,
            sep2=self.sep2,
        )

    def append_message(self, role, message):
        self.messages.append([role, message])


conv_vicuna_v1_1 = Conversation(
    system="A chat between a curious user and an artificial intelligence assistant. "
    "The assistant gives helpful, detailed, and polite answers to the user's questions.",
    roles=["USER", "ASSISTANT"],
    messages=[],
    offset=0,
    sep_style=SeparatorStyle.TWO,
    sep=" ",
    sep2=" ",
)


class ShareGPTPrompter:  # pylint: disable=too-few-public-methods
    """
    A prompter that generates prompts for the ShareGPT
    """

    def __init__(self, prompt_style=None):
        if prompt_style != PromptStyle.CHAT.value:
            raise ValueError(
                f"unsupported prompt_style for ShareGPTPrompter({prompt_style})"
            )

    # def match_prompt_style(self):
    #     if self.prompt_style == PromptStyle.chat.value:
    #         self.prompt_input = self.system_prompt + "USER: {instruction}\n{input}\nASSISTANT:"
    #         self.prompt_no_input = self.system_no_input_prompt + "USER: {instruction}\nASSISTANT:"
    #         self.response_split = "ASSISTANT:"

    def build_prompt(self, source) -> Generator[str, None, None]:
        # ignore the system prompt if provided
        if source[0]["from"] == "system":
            source.pop(0)

        if len(source) < 2:
            # If there isn't a back and forth conversation, ignore it
            # also happens on the data splitting leaving empty conversations
            raise IndexError

        conv = conv_vicuna_v1_1.copy()
        roles = {"human": conv.roles[0], "gpt": conv.roles[1]}

        try:
            # Apply prompt templates
            if (
                source[0]["from"] not in roles
                or roles[source[0]["from"]] != conv.roles[0]
            ):
                # Skip the first one if it is not from human
                source = source[1:]
        except IndexError as err:
            # sometimes there is a bing or system chat
            raise err

        conv.messages = []
        for j, sentence in enumerate(source):
            role = roles[sentence["from"]]
            assert role == conv.roles[j % 2]
            conv.append_message(role, sentence["value"])

        for part in conv.get_prompt():
            yield part
