import logging
from configuration_builder import ConfigurationBuilder
from simple_di_container import Container

from api import Api
from configuration.github_configuration import GithubConfiguration
from services.gitea_service import GiteaService
from services.ai.olama_ai_client import OllamaAIClient
from services.ai.ai_client import AIClient
from services.ai.openai_compatible_ai_client import OpenAICompatibleAIClient
from services.github_service import GithubService
from services.queue.memory_task_queue import InMemoryTaskQueue
from services.review_service import ReviewService

from configuration.web_configuration import WebConfiguration
from configuration.gitea_configuration import GiteaConfiguration
from configuration.llm_configuration import LLMConfiguration
from configuration.review_configuration import ReviewConfiguration
from configuration.llm_type import LLMType
from worker import Worker

#Initialize Container
container = Container()

# Initialize configuration
configurationBuilder = ConfigurationBuilder()
configurationBuilder.add_json_file("appsettings.json")
configurationBuilder.add_environment_variables()
configuration = configurationBuilder.build()

# Configure logger
logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s - %(message)s', level=logging.INFO)
logging.getLogger().setLevel(logging.INFO)


container.register(WebConfiguration, instance=WebConfiguration(**configuration["web"]))
container.register(GiteaConfiguration, instance=GiteaConfiguration(**configuration["gitea"]))
container.register(GithubConfiguration, instance=GithubConfiguration(**configuration["github"]))
container.register(LLMConfiguration, instance=LLMConfiguration(**configuration["llm"]))
container.register(ReviewConfiguration, instance=ReviewConfiguration(**configuration["review"]))

def llm_client_factory(services: Container) -> AIClient:
    llm_configuration : LLMConfiguration = services.resolve(LLMConfiguration)
    if (llm_configuration.type == LLMType.Ollama):
        return OllamaAIClient(llm_configuration)
    return OpenAICompatibleAIClient(llm_configuration)

container.register(AIClient, factory=llm_client_factory)
container.register(GiteaService)
container.register(GithubService)
container.register(ReviewService)
container.register(InMemoryTaskQueue)
container.register(Api)
container.register(Worker)


if __name__ == "__main__":
    worker : Worker = container.resolve(Worker)
    worker.start()
    api : Api = container.resolve(Api)
    api.start()