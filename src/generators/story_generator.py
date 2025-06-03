"""
Story Generator module for creating structured stories using LLMs.
"""

import logging
from typing import Union, Optional

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser, StrOutputParser

from src.models.schemas import StoryWithScenes

logger = logging.getLogger(__name__)

class StoryGenerator:
    """
    Class for generating structured stories using LangChain compatible LLMs.
    Can work with different LLM providers as long as they implement the BaseChatModel interface.
    """
    
    def __init__(self, llm: BaseChatModel):
        """
        Initialize the StoryGenerator with a LangChain compatible language model.
        
        Args:
            llm: A LangChain compatible language model like ChatGoogleGenerativeAI, ChatOpenAI, etc.
        """
        if llm is None:
            raise ValueError("LLM cannot be None. Please ensure a valid LangChain model is provided.")
        self.llm = llm
        self.parser = PydanticOutputParser(pydantic_object=StoryWithScenes)
        self.prompt_template = self._create_prompt_template()

    def _create_prompt_template(self) -> PromptTemplate:
        """
        Creates and returns the LangChain PromptTemplate for story generation.
        
        Returns:
            PromptTemplate configured for story generation
        """
        return PromptTemplate(
            template="""You are a highly creative and detail-oriented storytelling AI, specializing in crafting short stories perfect for visual adaptation.
            Your task is to generate a complete story and segment it into {scene_count} distinct scenes.

            **Crucial Instructions for Visual Consistency and Detail:**
            1.  **Overall Image Style:** Define a single, consistent, and highly descriptive visual style that will apply to *all* images/videos generated for this story. This style should be detailed enough for an image generation model.
            2.  **Character Consistency:** For each main character, provide a detailed and unchanging visual description of their appearance. This is vital for maintaining visual consistency across different scenes. Integrate these character descriptions into the `visual_description` for scenes where they appear.
            3.  **Scene Breakdown:**
                * Each scene must have a `visual_description` that is concise but extremely detailed, explicitly incorporating the `overall_image_style` and relevant `main_characters`' descriptions. Think of it as a detailed prompt for an image generation model.
                * The `narration_text` for each scene must be the exact dialogue or narration for that specific segment.
                * The combined `narration_text` from all scenes must form the complete and coherent `full_story_summary`.

            **Story Requirements:**
            * The story should be engaging and around {word_limit} words in total.
            * It must be exactly {scene_count} scenes.
            * Ensure logical flow and progression between scenes.

            **Subject for the Story:** {subject}

            **Output Format Instructions:**
            {format_instructions}""",
            input_variables=["subject", "word_limit", "scene_count"],
            partial_variables={"format_instructions": ""},
        )
        
    def generate_structured_story(self, subject: str, scene_count: int = 5, word_limit: Optional[int] = None) -> Union[StoryWithScenes, str]:
        """
        Generates a short story and breaks it into structured scenes using the provided LLM,
        outputting a Pydantic object.
        
        Args:
            subject: The subject or theme for the story
            scene_count: Number of scenes to create (default: 5)
            word_limit: Optional word limit for the story (defaults to scene_count * 50)
            
        Returns:
            A StoryWithScenes object or an error message string
        """
        if word_limit is None:
            word_limit = scene_count * 50  # Rough estimate for story length
            
        # Update format instructions right before invocation to ensure latest schema
        self.prompt_template.partial_variables = {"format_instructions": self.parser.get_format_instructions()}
            
        structured_story_chain = self.prompt_template | self.llm | self.parser
        logger.info(f"Generating structured story for subject: '{subject}' with {scene_count} scenes...")
        
        try:
            structured_output: StoryWithScenes = structured_story_chain.invoke({
                "subject": subject,
                "word_limit": word_limit,
                "scene_count": scene_count
            })
            logger.info("Structured story generated successfully!")
            return structured_output
        except Exception as e:
            error_msg = f"Error during structured story generation: {e}"
            logger.error(error_msg)
            try:
                # Attempt to get raw output for debugging
                raw_output_chain = self.prompt_template | self.llm | StrOutputParser()
                raw_output = raw_output_chain.invoke({
                    "subject": subject,
                    "word_limit": word_limit,
                    "scene_count": scene_count
                })
                logger.debug("\nRaw LLM output (for debugging parsing issues):\n%s", raw_output)
            except Exception as inner_e:
                logger.error(f"Could not get raw LLM output for debugging: {inner_e}")
                
            return f"Error: Could not generate structured story for '{subject}'. Details: {e}"
