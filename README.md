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
    Responder.get_answers_from_documents('my-token','How easy is Cape to use', document_ids=None,text ="Cape is super easy to use !")
   ```
   * As a service : `python3 -m cape_webservices.run`
   * As a docker container : `$ docker run -p 5050:5050 bloomsburyai/cape`
   * As an app with UI (more info below)
   * As a distributed cluser (more info below)

   
## Tutorials

### Quick start guide with docker

 `docker run -p 5050:5050 bloomsburyai/cape ipython3`

## API Reference


## Library Reference

