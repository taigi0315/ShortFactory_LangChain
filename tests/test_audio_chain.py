import pytest

from chains.audio_chain import AudioChain


def test_audio_chain_initialization():
    chain = AudioChain()
    assert chain is not None
    assert "Amber" in chain.voice_map
    assert "shocked" in chain.emotion_presets


def test_voice_mapping():
    chain = AudioChain()
    assert chain.voice_map["Amber"] == "Rachel"
    assert chain.voice_map["Jade"] == "Bella"
    assert chain.voice_map["Liam"] == "Adam"
    assert chain.voice_map["Noah"] == "Antoni"


def test_emotion_presets():
    chain = AudioChain()
    shocked_preset = chain.emotion_presets["shocked"]
    assert shocked_preset["stability"] == 0.3
    assert shocked_preset["style"] == 0.8
