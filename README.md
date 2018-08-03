# cape-webservices [![CircleCI](https://circleci.com/gh/bloomsburyai/cape-webservices.svg?style=svg&circle-token=fa3cd468ad24f3f22e56daaed4ba32fee60e0918)](https://circleci.com/gh/bloomsburyai/cape-webservices)
Entrypoint for all backend cape webservices.

## TL; DR

Cape is a suite of libraries to use the latest in AI to ask questions in plain english to documents.
As long as the answer is in the documents and the model is sufficiently trained, cape will return the answer.
It was done with love by the team behind Bloomsbury AI, completely refactored to make it Open Source friendly for all expertise levels.


There are several ways to use Cape : 
    
   * As a python library :
   ``` 
    from cape_responder.responder_core import Responder
    Responder.get_answers_from_documents('my-token','How easy is Cape to use', text ="Cape is an open source large-scale question answering system and is super easy to use!")
   ```
   * As a service : `python3 -m cape_webservices.run`
   * As a Docker container : `docker run -p 5050:5050 bloomsburyai/cape`
   * As an app with UI (more info below)
   * As a distributed cluster (more info below)

   
## Tutorials

### Quick Start Guide with Docker

1. Pull the latest version of the Docker image (it will take a few moments to download all dependencies and a machine reading model):
`docker pull bloomsburyai/cape`

1. Run the Docker container and launch an IPython console within it using the following command: `docker run -ti -p 5050:5050 -p 5051:5051 bloomsburyai/cape ipython3`

1. Import Responder: `from cape_responder.responder_core import Responder`

1. Ask a question and store the response (which is a list of answers) and display the first answer using: `response = Responder.get_answers_from_documents('my-token','How easy is Cape to use?', text="Cape is an open source large-scale question answering system and is super easy to use!"); print(response[0]['answerText'])`

1. If you are interested in understanding a bit more about what the response looks like, display the full response using: `print(response)`


## API Reference


## Library Reference

