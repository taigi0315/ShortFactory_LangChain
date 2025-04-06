import pytest

from chains.gossip_chain import DialogueLine, GossipChain


def test_gossip_chain_initialization():
    chain = GossipChain()
    assert chain is not None
    assert chain.llm is not None
    assert chain.parser is not None


def test_dialogue_line_model():
    line = DialogueLine(
        character="Amber",
        emotion="shocked",
        text="Wait — she invited her ex to her birthday?!",
    )
    assert line.character == "Amber"
    assert line.emotion == "shocked"
    assert line.text == "Wait — she invited her ex to her birthday?!"
