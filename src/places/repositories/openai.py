import logging

from pydantic_ai import Agent
from pydantic_ai.models.openai import OpenAIModel

from src.places.exceptions import OpenAIError
from src.places.schemas.openai import PlaceDetailResponse
from src.settings import settings


logger = logging.getLogger(__name__)


class DescriptionOpenAIRepository:
    def __init__(self):
        self.agent = self._create_agent()

    @staticmethod
    def _create_agent() -> Agent:
        """
        Creates and returns an Agent object to interact with OpenAI.
        """
        model = OpenAIModel(
            model_name=settings.pydantic_ai_model,
            api_key=settings.openai_api_key,
        )
        return Agent(
            model=model,
            result_type=PlaceDetailResponse,
            system_prompt='You are a helpful assistant.',
        )

    async def get_place_detail(self, prompt: str) -> PlaceDetailResponse:
        """
        Interacts with the OpenAI API through an agent and
        returns the result as a DescriptionResponse.
        """
        try:
            response = await self.agent.run(user_prompt=prompt)
            print(response)
            return PlaceDetailResponse(
                description=response.data.description, photo_url=response.data.photo_url
            )
        except Exception as e:
            logger.error(f'Error while interacting with OpenAI API: {e}')
            raise OpenAIError()
