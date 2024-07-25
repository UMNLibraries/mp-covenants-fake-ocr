# mp-covenants-fake-ocr

This AWS Lambda function is part of [Mapping Prejudice's](https://mappingprejudice.umn.edu/) Deed Machine application. This component is designed to mimic actions of OCR step, but skip actual OCR, to avoid needing to re-OCR files that have already been OCRed, which is relatively expensive. The function opens a previously created OCR JSON saved to s3 and passes data about it on to the next step. This lambda is only used for DeedPageProcessorFAKEOCR, which is run to correct errors in post-OCR stages of the main DeedPageProcessor Step Function.

The [Deed Machine](https://github.com/UMNLibraries/racial_covenants_processor/) is a multi-language set of tools that use OCR and crowdsourced transcription to identify racially restrictive covenant language, then map the results.

The Lambda components of the Deed Machine are built using Amazon's Serverless Application Model (SAM) and the AWS SAM CLI tool.

## Key links
- [License](https://github.com/UMNLibraries/racial_covenants_processor/blob/main/LICENSE)
- [Component documentation](https://the-deed-machine.readthedocs.io/en/latest/modules/lambdas/mp-covenants-fake-ocr.html)
- [Documentation home](https://the-deed-machine.readthedocs.io/en/latest/)
- [Downloadable Racial covenants data](https://github.com/umnlibraries/mp-us-racial-covenants)
- [Mapping Prejudice main site](https://mappingprejudice.umn.edu/)

## Software development requirements
- Pipenv (Can use other virtual environments, but will require fiddling on your part)
- AWS SAM CLI
- Docker
- Python 3

## Quickstart commands

To build the application:

```bash
pipenv install
pipenv shell
sam build
```

To rebuild and deploy the application:

```bash
sam build && sam deploy
```

To run tests:

```bash
pytest
```