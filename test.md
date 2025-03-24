# Running Tests and Generating Coverage Report

## Combined Coverage Report

- To run the tests and generate a combined coverage report, use the following command in Command Prompt:
```bash
  set PYTHONPATH=src;src/api_service;workflow && pytest tests --cov=src --cov=workflow --cov-report=term-missing --cov-report=html
```
- If you visit the folder tests/, it contains all the comprehensive testing functions to check many components of the code like the API endpoints, functions, docker containers, LLM outputs and many more. This is still a work in progress and we hope to make our system more robust by adding more testing functions.

- But, if you want to check the componnents individually, just follow the isntructions below:

## For checking whether the model endpoint is working or not and if we are getting outputs from our fine-tuned model hosted in Google Cloud, use this code:

 ```bash
pytest tests/test_model_endpoint.py
 ```
## For testing API endpoints:

- In test_api.py, we are testing API endpoints to ensure they function correctly and handle inputs and errors gracefully. 
- We are validating input fields, checking user authentication and authorization, and verifying that the responses are in the expected format.
- We are also testing integration with external services like OpenAI and SERP API to ensure they work seamlessly. 
- We are ensuring proper error handling for scenarios like missing credentials or invalid data, and testing how the APIs perform under different conditions, such as larger payloads or concurrent requests. 
- To run this, use this code:

```bash
pytest tests/test_api.py
 ```

## For testing functionality of emails:

- In test_emails.py, the tests focus on validating the functionality of email creation and sending processes. 
- These include verifying that email formatting is correct, attachments are properly added, and the email body contains the expected content. 
- The tests also cover edge cases, such as handling invalid recipient addresses, missing attachments, and failures when the email server is unavailable. 
- Simulated email sending ensures the application interacts correctly with the SMTP server without actually sending emails during the test execution.
- To run this, use this code:

```bash
pytest tests/test_emails.py
 ```
## To test the working pipeline:

- This testing suite is actually tests the main fucntionalities of our working process and thus covers over 50% of test coverage.
- In test_workflow.py, the tests validate the functionality of the WorkflowManager class and its methods. 
- To run the pipeline from data extraction, cleaning , vecotirization,  the dvc pipeline and the frontend api service along with running Docker services, and executing the workflow stages. 
- These tests ensure each stage in the workflow is executed in the correct sequence and that appropriate logging occurs for both successes and errors. 
- Simulated runs of Docker services and error handling scenarios are tested to confirm the robustness of the workflow management process. The tests verify that the main menu interaction handles user inputs effectively.
- To run this, use this code:

```bash
pytest tests/test_workflow.py
 ```

## To test the retrieval pipeline (It is still in the works):

- In test_retrieval.py, the tests focus on the functionality of the retrieval module, which includes web scraping, file handling, and API integrations. 
- Key functionalities tested include fetching organic results from Google Custom Search API, scraping website content, combining scraped data with OpenAI API responses, saving files to OpenAI, and managing bots and threads. 
- The tests also cover utility functions like sanitizing filenames, compressing audio files, and converting audio to text. 
- Mocking is extensively used to simulate API responses and ensure the reliability of the module without external dependencies. 



